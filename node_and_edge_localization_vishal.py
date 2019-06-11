import cv2
import numpy as np
import os
import shutil
import time
from imutils import paths
import video_operations_2 as vo2
import matcher as mt
from graph import Graph, Edge, Node, FloorMap, load_graph


class NodeEdgeMatching:
    matched_path = []

    # matched is array of dictionary of type { "node: Node", "edge: Edge", "confidence: int",
    # "last_matched_i_with_j: int", "last_matched_j: int", "no_of_frames_to_match: int", "edge_ended: bool"}

    def __init__(self, graph_obj: Graph, query_video_distinct_frames: vo2.DistinctFrames):
        some_query_img_objects = []
        some_query_img_objects.append(query_video_distinct_frames.get_object(0))
        # img_objects_list contains 3 elements
        nodes_matched = self.match_node_with_frames(some_query_img_objects, graph_obj)
        self.find_edge_with_nodes(nodes_matched, query_video_distinct_frames, 0)
        return

    def match_node_with_frames(self, some_query_img_objects: list, graph_obj: Graph):
        """returns matched nodes using query_video_frames"""
        search_list = graph_obj.Nodes
        node_confidence = []
        # node_confidence is list of (node.identity:int , confidence:int , total_fraction_matched:float)
        for img_obj in some_query_img_objects:
            for node in search_list:
                node_images: vo2.DistinctFrames = node.node_images
                if node_images is not None:
                    for data_obj in node_images.get_objects():
                        image_fraction_matched = mt.SURF_match_2(img_obj.get_elements(), data_obj.get_elements(),
                                                                 2500, 0.7)
                        if image_fraction_matched > 0.2:
                            if len(node_confidence) > 0 and node_confidence[-1][0] == node.identity:
                                entry = node_confidence[-1]
                                node_confidence[-1] = (node.identity, entry[1] + 1, entry[2] + image_fraction_matched)
                                # print(str(node.identity) + " matched by " + str(image_fraction_matched))
                            else:
                                node_confidence.append((node.identity, 1, image_fraction_matched))
        sorted(node_confidence, key=lambda x: (x[1], x[2]), reverse=True)
        final_node_list = []
        for entry in node_confidence:
            final_node_list.append(graph_obj.get_node(entry[0]))
        return final_node_list

    def match_edge_with_frame(self, possible_edge, i: int, query_video_ith_frame: vo2.ImgObj):
        # possible edge here is passed as reference
        print("yo")
        j = possible_edge["last_matched_j"]
        jmax = possible_edge["last_matched_j"] + possible_edge["no_of_frames_to_match"]
        while j < jmax and j < possible_edge["edge"].distinct_frames.no_of_frames:
            print(j)
            match, maxmatch = None, 0
            edge = possible_edge["edge"]
            img_obj_from_edge = edge.distinct_frames.get_object(j)
            image_fraction_matched = mt.SURF_match_2(img_obj_from_edge, query_video_ith_frame, 2500, 0.7)
            if image_fraction_matched > 0.15:
                if image_fraction_matched > maxmatch:
                    match, maxmatch = j, image_fraction_matched
            j = j + 1
        if match is None:
            possible_edge["confidence"] = possible_edge["confidence"] - 1
            possible_edge["no_of_frames_to_match"] = possible_edge["no_of_frames_to_match"] + 1
        else:
            possible_edge["last_matched_j"] = match
            possible_edge["last_matched_i_with_j"] = i
        if j == (possible_edge["edge"].distinct_frames.no_of_frames - 1):
            possible_edge["edge_ended"] = True

    def find_edge_with_nodes(self, nodes_matched: list, query_video_distinct_frames: vo2.DistinctFrames,
                             i_at_matched_node: int):
        possible_edges = []
        for node in nodes_matched:
            for edge in node.links:
                if edge.distinct_frames is not None:
                    possible_edges.append({
                        "node": node,
                        "edge": edge,
                        "confidence": 0,
                        "last_matched_i_with_j": i_at_matched_node - 1,
                        "last_matched_j": -1,
                        "no_of_frames_to_match": 3,
                        "edge_ended": False
                    })
        # i_at_matched_node is 0 means that there can be multiple nodes because query video is just started querying for path matching
        is_edge_found = False
        is_edge_partially_found = False
        found_edge = None
        i = i_at_matched_node
        max_confidence = 0
        print("po")
        while True:
            print("so" + str(i))
            if is_edge_found or is_edge_partially_found:
                break
            for possible_edge in possible_edges:
                if possible_edge["confidence"] < max_confidence:
                    continue
                print("ho")
                i = possible_edge["last_matched_i_with_j"] + 1
                if i >= query_video_distinct_frames.no_of_frames():
                    is_edge_partially_found = True
                    found_edge = possible_edge
                    break
                if possible_edge["edge_ended"]:
                    # edge is found
                    is_edge_found = True
                    found_edge = possible_edge
                    break
                query_video_ith_frame = query_video_distinct_frames.get_object(i)
                self.match_edge_with_frame(possible_edge, i, query_video_ith_frame)
                max_confidence = possible_edge["confidence"]
                print(i)
        if is_edge_found:
            self.matched_path.append(found_edge)
            next_node_identity = found_edge["edge"].dest
            next_matched_nodes = []
            # next_matched_nodes will only contain one node which is the the nest node
            for Nd in nodes_matched:
                if Nd.identity == next_node_identity:
                    next_matched_nodes.append(Nd)
            self.find_edge_with_nodes(next_matched_nodes, query_video_distinct_frames, i)
            # i = found_edge["last_matched_i_with_j"] + 1
        elif is_edge_partially_found:
            self.matched_path.append(found_edge)
            j = found_edge["last_matched_j"]
            last_jth_matched_img_obj = found_edge["edge"].distinct_frames.get_object(j)
            print("This edge is partially found upto " + last_jth_matched_img_obj.time_stamp)

    def print_path(self):
        for found_edge in self.matched_path:
            edge: Edge = found_edge["edge"]
            print("edge" + edge.src + "_" + edge.dest)

graph_obj: Graph = load_graph()
query_video_frames1 = vo2.save_distinct_ImgObj("testData/vishal_open_camera_Videos/edge_0_1.mp4", "query_distinct_frame", 2, True)
node_edge_matching_obj = NodeEdgeMatching(graph_obj, query_video_frames1)
node_edge_matching_obj.print_path()