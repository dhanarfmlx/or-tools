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
        self._num_vehicles = 4

        self._city_block = CityBlock()

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
        self._locations = [(
            loc[0]*self.city_block.width,
            loc[1]*self.city_block.height) for loc in locations]
        self._depot = 0

    @property
    def num_vehicles(self):
        """Gets number of vehicles"""
        return self._num_vehicles

    @property
    def city_block(self):
        """Gets a city block"""
        return self._city_block

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

    def manhattan_distance(self, from_node, to_node):
        """Computes the Manhattan distance between two nodes"""
        return (abs(self.locations[from_node][0] - self.locations[to_node][0]) +
                abs(self.locations[from_node][1] - self.locations[to_node][1]))

#######################
# Problem Constraints #
#######################
class CreateDistanceCallback(object): # pylint: disable=too-few-public-methods
    """Creates callback to return distance between points."""
    def __init__(self, data):
        """Initializes the distance matrix."""
        self._distance = {}

        # precompute distance between location to have distance callback in O(1)
        for from_node in xrange(data.num_locations):
            self._distance[from_node] = {}
            for to_node in xrange(data.num_locations):
                if from_node == to_node:
                    self._distance[from_node][to_node] = 0
                else:
                    self._distance[from_node][to_node] = (
                        data.manhattan_distance(from_node, to_node))

    def distance(self, from_node, to_node):
        """Returns the manhattan distance between the two nodes"""
        return self._distance[from_node][to_node]

def add_distance_dimension(routing, dist_callback):
    """Add Global Span constraint"""
    distance = "Distance"
    routing.AddDimension(
        dist_callback,
        0, # null slack
        3000, # maximum distance per vehicle
        True, # start cumul to zero
        distance)
    distance_dimension = routing.GetDimensionOrDie(distance)
    # Try to minimize the max distance among vehicles.
    # /!\ It doesn't mean the standard deviation is minimized
    distance_dimension.SetGlobalSpanCostCoefficient(100)

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
        total_dist = 0
        for vehicle_id in xrange(self.data.num_vehicles):
            index = self.routing.Start(vehicle_id)
            plan_output = 'Route for vehicle {0}:\n'.format(vehicle_id)
            route_dist = 0
            while not self.routing.IsEnd(index):
                node_index = self.routing.IndexToNode(index)
                next_node_index = self.routing.IndexToNode(
                    self.assignment.Value(self.routing.NextVar(index)))
                route_dist += self.data.manhattan_distance(node_index, next_node_index)
                plan_output += ' {node_index} -> '.format(
                    node_index=node_index)
                index = self.assignment.Value(self.routing.NextVar(index))

            node_index = self.routing.IndexToNode(index)
            total_dist += route_dist
            plan_output += ' {node_index}\n'.format(
                node_index=node_index)
            plan_output += 'Distance of the route {0}: {dist}\n'.format(
                vehicle_id,
                dist=route_dist)
            print(plan_output)
        print('Total Distance of all routes: {dist}'.format(dist=total_dist))

########
# Main #
########
def main():
    """Entry point of the program"""
    # Instanciate the data problem.
    data = DataProblem()

    # Create Routing Model
    routing = pywrapcp.RoutingModel(data.num_locations, data.num_vehicles, data.depot)
    # Define weight of each edge
    dist_callback = CreateDistanceCallback(data).distance
    routing.SetArcCostEvaluatorOfAllVehicles(dist_callback)
    add_distance_dimension(routing, dist_callback)

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
