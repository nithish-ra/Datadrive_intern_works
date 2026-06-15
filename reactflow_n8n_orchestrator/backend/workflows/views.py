from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Workflow
import requests

@api_view(['POST'])
def save_workflow(request):
    data = request.data
    
    # 1. Save the visual blueprint to your database (Restored from your original code!)
    workflow = Workflow.objects.create(
        nodes=data.get('nodes', []),
        edges=data.get('edges', [])
    )
    
    nodes = data.get('nodes', [])
    edges = data.get('edges', [])
    
    # 2. Create a quick lookup dictionary for the nodes
    node_dict = {node['id']: node for node in nodes}
    
    # 3. Find the exact starting point
    start_node = next((n for n in nodes if n['data'].get('label') == 'Start Trigger'), None)
    if not start_node:
        return Response({"error": "No Start Trigger found on canvas"}, status=400)

    # 4. The Boss Level Logic: Trace the visual path using edges
    execution_plan = []
    current_node_id = start_node['id']

    while current_node_id:
        # Find the line (edge) where the current node is the source
        next_edge = next((e for e in edges if e['source'] == current_node_id), None)
        
        if next_edge:
            # Follow the line to the target node
            next_node_id = next_edge['target']
            next_node = node_dict.get(next_node_id)
            
            if next_node:
                # Add the node's data to our strict execution sequence
                execution_plan.append(next_node['data'])
                current_node_id = next_node_id
            else:
                break # Node missing, stop tracing
        else:
            break # No more connected lines, end of the workflow

    # 5. Print to terminal to verify the visual sequence was captured
    print("--- DYNAMIC EXECUTION PLAN ---")
    for step, task in enumerate(execution_plan):
        print(f"Step {step + 1}: {task.get('label')}")
    print("------------------------------")

    # 6. Forward the execution data to n8n
    # Make sure this points to your newly duplicated "V2" workflow Webhook URL!
    n8n_webhook_url = "http://localhost:5678/webhook-test/9b9036fb-7943-42c0-8c18-f5f27d0a15f6"
    
    # We now send the strictly ordered plan to n8n!
    payload = {
        "raw_canvas": data,
        "execution_plan": execution_plan
    }
    
    try:
        n8n_response = requests.post(n8n_webhook_url, json=payload)
        
        return Response({
            "status": "success", 
            "message": "Workflow saved and Dynamic Plan sent to n8n!", 
            "workflow_id": workflow.id,
            "execution_sequence": [task.get('label') for task in execution_plan],
            "n8n_status": n8n_response.status_code
        })
    except Exception as e:
        return Response({
            "status": "partial_success",
            "message": "Generated dynamic plan and saved to DB, but failed to reach n8n.",
            "error": str(e)
        })