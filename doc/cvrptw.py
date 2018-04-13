#!/usr/bin/env python
# This Python file uses the following encoding: utf-8
# Copyright 2015 Tin Arm Engineering AB
# Copyright 2018 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Vehicle Routing Problem (VRP).
   This is a sample using the routing library python wrapper to solve a VRP problem.
   A description of the problem can be found here:
   http://en.wikipedia.org/wiki/Vehicle_routing_problem.

   Distances are in meters and time in seconds.

   Manhattan average block: 750ft x 264ft -> 228m x 80m
   src: https://nyti.ms/2GDoRIe "NY Times: Know Your distance"
   here we use: 114m x 80m city block
"""

from __future__ import print_function
from six.moves import xrange
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

###########################
# Problem Data Definition #
###########################
class Vehicle():
    """Stores the property of a vehicle"""
    def __init__(self):
        """Initializes the vehicle properties"""
        self._capacity = 15
        # Travel speed: 5km/h to convert in m/s
        self._speed = 5 / 3.6

    @property
    def capacity(self):
        """Gets vehicle capacity"""
        return self._capacity

    @property
    def speed(self):
        """Gets the average travel speed of a vehicle"""
        return self._speed

class CityBlock():
    """City block definition"""
    @property
    def width(self):
        """Gets Block size West to East"""
        return 228/2

    @property
    def height(self):
        """Gets Block size North to South"""
        return 80

class DataProblem():
    """Stores the data for the problem"""
    def __init__(self):
        """Initializes the data for the problem"""
        self._vehicle = Vehicle()
        self._num_vehicles = 4

        # Locations in block unit
        locations = \
                [(4, 4), # depot
                 (2, 0), (8, 0), # row 0
                 (0, 1), (1, 1),
                 (5, 2), (7, 2),
                 (3, 3), (6, 3),
                 (5, 5), (8, 5),
                 (1, 6), (2, 6),
                 (3, 7), (6, 7),
                 (0, 8), (7, 8)]
        # locations in meters using the block dimension defined
        city_block = CityBlock()
        self._locations = [(
            loc[0]*city_block.width,
            loc[1]*city_block.height) for loc in locations]

        self._depot = 0

        self._demands = \
            [0, # depot
             1, 1, # row 0
             2, 4,
             2, 4,
             8, 8,
             1, 2,
             1, 2,
             4, 4,
             8, 8]

        self._time_windows = \
            [(0,0),
             (0, 8000), (0, 8000), # row 0
             (0, 8000), (0, 8000),
             (0, 8000), (0, 8000),
             (0, 8000), (0, 8000),
             (0, 8000), (0, 8000),
             (0, 8000), (0, 8000),
             (0, 8000), (0, 8000),
             (0, 8000), (0, 8000)]

    @property
    def vehicle(self):
        """Gets a vehicle"""
        return self._vehicle

    @property
    def num_vehicles(self):
        """Gets number of vehicles"""
        return self._num_vehicles

    @property
    def locations(self):
        """Gets locations"""
        return self._locations

    @property
    def num_locations(self):
        """Gets number of locations"""
        return len(self.locations)

    @property
    def depot(self):
        """Gets depot location index"""
        return self._depot

    @property
    def demands(self):
        """Gets demands at each location"""
        return self._demands

    @property
    def time_per_demand_unit(self):
        """Gets the time (in s) to load a demand"""
        return 5 * 60 # 5 minutes/unit

    @property
    def time_windows(self):
        """Gets (start time, end time) for each locations"""
        return self._time_windows

#######################
# Problem Constraints #
#######################
def manhattan_distance(position_1, position_2):
    """Computes the Manhattan distance between two points"""
    return (abs(position_1[0] - position_2[0]) +
            abs(position_1[1] - position_2[1]))

class CreateDistanceEvaluator(object): # pylint: disable=too-few-public-methods
    """Creates callback to return distance between points."""
    def __init__(self, data):
        """Initializes the distance matrix."""
        self._distances = {}

        # precompute distance between location to have distance callback in O(1)
        for from_node in xrange(data.num_locations):
            self._distances[from_node] = {}
            for to_node in xrange(data.num_locations):
                if from_node == to_node:
                    self._distances[from_node][to_node] = 0
                else:
                    self._distances[from_node][to_node] = (
                        manhattan_distance(
                            data.locations[from_node],
                            data.locations[to_node]))

    def distance_evaluator(self, from_node, to_node):
        """Returns the manhattan distance between the two nodes"""
        return self._distances[from_node][to_node]

def add_distance_dimension(routing, distance_evaluator):
    """Add Global Span constraint"""
    distance = "Distance"
    routing.AddDimension(
        distance_evaluator,
        0, # null slack
        3000, # maximum distance per vehicle
        True, # start cumul to zero
        distance)
    distance_dimension = routing.GetDimensionOrDie(distance)
    # Try to minimize the max distance among vehicles.
    # /!\ It doesn't mean the standard deviation is minimized
    distance_dimension.SetGlobalSpanCostCoefficient(100)

class CreateDemandEvaluator(object): # pylint: disable=too-few-public-methods
    """Creates callback to get demands at each location."""
    def __init__(self, data):
        """Initializes the demand array."""
        self._demands = data.demands

    def demand_evaluator(self, from_node, to_node):
        """Returns the demand of the current node"""
        del to_node
        return self._demands[from_node]

def add_capacity_constraints(routing, data, demand_evaluator):
    """Adds capacity constraint"""
    capacity = "Capacity"
    routing.AddDimension(
        demand_evaluator,
        0, # null capacity slack
        data.vehicle.capacity,
        True, # start cumul to zero
        capacity)

class CreateTimeEvaluator(object):
    """Creates callback to get total times between locations."""
    @staticmethod
    def service_time(data, node):
        """Gets the service time for the specified location."""
        return data.demands[node] * data.time_per_demand_unit

    @staticmethod
    def travel_time(data, from_node, to_node):
        """Gets the travel times between two locations."""
        if from_node == to_node:
            travel_time = 0
        else:
            travel_time = manhattan_distance(
                data.locations[from_node],
                data.locations[to_node]) / data.vehicle.speed
        return travel_time

    def __init__(self, data):
        """Initializes the total time matrix."""
        self._total_time = {}
        # precompute total time to have time callback in O(1)
        for from_node in xrange(data.num_locations):
            self._total_time[from_node] = {}
            for to_node in xrange(data.num_locations):
                if from_node == to_node:
                    self._total_time[from_node][to_node] = 0
                else:
                    self._total_time[from_node][to_node] = int(
                        self.service_time(data, from_node) +
                        self.travel_time(data, from_node, to_node))
        print('transit time: {0}'.format(self._total_time))

    def time_evaluator(self, from_node, to_node):
        """Returns the total time between the two nodes"""
        return self._total_time[from_node][to_node]

def add_time_window_constraints(routing, data, time_evaluator):
    """Add Global Span constraint"""
    time = "Time"
    routing.AddDimension(
        time_evaluator,
        3600*8, # null slack
        3600*8, # maximum time per vehicle
        True, # start cumul to zero
        time)
    time_dimension = routing.GetDimensionOrDie(time)
    # Try to minimize the max distance among vehicles.
    # /!\ It doesn't mean the standard deviation is minimized
    time_dimension.SetGlobalSpanCostCoefficient(100)
    #for count, time_window in enumerate(data.time_windows):
    #    time_dimension.CumulVar(count).SetRange(time_window[0], time_window[1])

###########
# Printer #
###########
class ConsolePrinter():
    """Print solution to console"""
    def __init__(self, data, routing, assignment):
        """Initializes the printer"""
        self._data = data
        self._routing = routing
        self._assignment = assignment

    @property
    def data(self):
        """Gets problem data"""
        return self._data

    @property
    def routing(self):
        """Gets routing model"""
        return self._routing

    @property
    def assignment(self):
        """Gets routing model"""
        return self._assignment

    def print(self):
        """Prints assignment on console"""
        # Inspect solution.
        #distance_dimension = routing.GetDimensionOrDie('Distance')
        capacity_dimension = self.routing.GetDimensionOrDie('Capacity')
        time_dimension = self.routing.GetDimensionOrDie('Time')
        total_dist = 0
        total_time = 0
        for vehicle_id in xrange(self.data.num_vehicles):
            index = self.routing.Start(vehicle_id)
            plan_output = 'Route for vehicle {0}:\n'.format(vehicle_id)
            route_dist = 0
            route_load = 0
            route_time = 0
            while not self.routing.IsEnd(index):
                node_index = self.routing.IndexToNode(index)
                next_node_index = self.routing.IndexToNode(
                    self.assignment.Value(self.routing.NextVar(index)))
                route_dist += manhattan_distance(
                    self.data.locations[node_index],
                    self.data.locations[next_node_index])
                load_var = capacity_dimension.CumulVar(index)
                route_load = self.assignment.Value(load_var)
                time_var = time_dimension.CumulVar(index)
                route_time = self.assignment.Value(time_var)
                #tmin = self.assignment.Min(time_var)
                #tmax = self.assignment.Max(time_var)
                plan_output += ' {node_index} Load({load}) Time({time}) -> '.format(
                    node_index=node_index,
                    load=route_load,
                    time=route_time)
                index = self.assignment.Value(self.routing.NextVar(index))

            node_index = self.routing.IndexToNode(index)
            load_var = capacity_dimension.CumulVar(index)
            route_load = self.assignment.Value(load_var)
            time_var = time_dimension.CumulVar(index)
            route_time = self.assignment.Value(time_var)
            total_dist += route_dist
            total_time += route_time
            plan_output += ' {node_index} Load({load}) Time({time})\n'.format(
                node_index=node_index,
                load=route_load,
                time=route_time)
            plan_output += 'Distance of the route {0}: {dist}\n'.format(
                vehicle_id,
                dist=route_dist)
            plan_output += 'Load of the route {0}: {load}\n'.format(
                vehicle_id,
                load=route_load)
            plan_output += 'Time of the route {0}: {time}\n'.format(
                vehicle_id,
                time=route_time)
            print(plan_output)
        print('Total Distance of all routes: {dist}'.format(dist=total_dist))
        print('Total Time of all routes: {time}'.format(time=total_time))

########
# Main #
########
def main():
    """Entry point of the program"""
    # Instantiate the data problem.
    data = DataProblem()

    # Create Routing Model
    routing = pywrapcp.RoutingModel(data.num_locations, data.num_vehicles, data.depot)
    # Define weight of each edge
    distance_evaluator = CreateDistanceEvaluator(data).distance_evaluator
    routing.SetArcCostEvaluatorOfAllVehicles(distance_evaluator)
    # Add Capacity constraint
    demand_evaluator = CreateDemandEvaluator(data).demand_evaluator
    add_capacity_constraints(routing, data, demand_evaluator)
    # Add Time constraint
    time_evaluator = CreateTimeEvaluator(data).time_evaluator
    add_time_window_constraints(routing, data, time_evaluator)

    # Setting first solution heuristic (cheapest addition).
    search_parameters = pywrapcp.RoutingModel.DefaultSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    # Solve the problem.
    assignment = routing.SolveWithParameters(search_parameters)
    printer = ConsolePrinter(data, routing, assignment)
    printer.print()

if __name__ == '__main__':
    main()
