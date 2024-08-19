from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost",  # If you are running frontend on localhost
    "http://localhost:3001",  # Default port for Create React App
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Node(BaseModel):
    id: str = Field(..., description="The unique identifier of the node")
    type: str = Field(..., description="The type of the node")
    data: dict = Field(..., description="The data associated with the node")
    position: dict = Field(..., description="The position of the node on the canvas")

class Edge(BaseModel):
    id: str = Field(..., description="The unique identifier of the edge")
    source: str = Field(..., description="The source node ID")
    target: str = Field(..., description="The target node ID")

class Pipeline(BaseModel):
    nodes: List[Node] = Field(..., description="List of nodes in the pipeline")
    edges: List[Edge] = Field(..., description="List of edges in the pipeline")

@app.post("/pipelines/parse")
async def parse_pipeline(pipeline: Pipeline):
    try:
        num_nodes = len(pipeline.nodes)
        num_edges = len(pipeline.edges)

        # Check for DAG
        graph = {node.id: [] for node in pipeline.nodes}
        for edge in pipeline.edges:
            graph[edge.source].append(edge.target)

        def has_cycle(v, visited, rec_stack):
            visited[v] = True
            rec_stack[v] = True

            for neighbor in graph[v]:
                if not visited[neighbor]:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif rec_stack[neighbor]:
                    return True

            rec_stack[v] = False
            return False

        visited = {node: False for node in graph}
        rec_stack = {node: False for node in graph}
        is_dag = not any(has_cycle(node, visited, rec_stack) for node in graph if not visited[node])

        return {
            "num_nodes": num_nodes,
            "num_edges": num_edges,
            "is_dag": is_dag
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
