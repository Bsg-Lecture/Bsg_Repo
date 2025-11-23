from mitmproxy import http, websocket, ctx, tcp
import json

def print_dict(d, indent = 0, msg = None):
    # Iterate over the dictionary items
    for key, value in d.items():
        if isinstance(value, dict):
            # If the value is a dictionary, call the function recursively
            print(f'{" " * indent}{key}:')
            print_dict(value, indent + 4)  # Increase the indentation for nested dicts
        else:
            # Print the key-value pair
            print(f'{" " * indent}{key}:   {value}')
        if key == 'password':
            d[key] = value
        if key == 'certificateChain':
            msg.drop()

# This function is called when an HTTP request is captured
def request(flow: http.HTTPFlow) -> None:
    print("=== HTTP REQUEST ===")
    print(f"Host: {flow.request.host}")
    print(f"Path: {flow.request.path}")
    print(f"Method: {flow.request.method}")
    print(f"Headers: {flow.request.headers}")
    print(f"Content: {flow.request.text}")
    print("====================\n")

# This function is called when an HTTP response is captured
def response(flow: http.HTTPFlow) -> None:
    print("=== HTTP RESPONSE ===")
    print(f"Status Code: {flow.response.status_code}")
    print(f"Headers: {flow.response.headers}")
    print(f"Content: {flow.response.text}")
    print("====================\n")

# This function is called when a WebSocket connection is established
def websocket_handshake(flow: http.HTTPFlow):
    print(f"=== WEBSOCKET HANDSHAKE ===")
    print(f"Client to {flow.request.host} initiated WebSocket connection")
    print("===========================\n")

def websocket_message(flow: http.HTTPFlow):
    message = flow.websocket.messages[-1] # Get the last message
    direction = "CLIENT -> SERVER" if message.from_client else "SERVER -> CLIENT"
    
    print(f"=== WEBSOCKET MESSAGE ===")
    print(f"{direction}")
    print(f"Message received: {message.content}")
    
    # Assuming the content is a JSON-like string, convert it to a dictionary
    try:
        content_dict = json.loads(message.content)
        # Get the indexes of dictionaries in content_dict
        indexes = [i for i, element in enumerate(content_dict) if isinstance(element, dict)]

        for index in indexes:
            print(f'Dictionary at index {index}:')
            print_dict(content_dict[index], msg=message)
        message.text = json.dumps(content_dict)

        # Convert the modified dictionary back to a JSON string
        print(f"Message sent: {message.content}")
    except json.JSONDecodeError:
        print("Message content is not a valid JSON")
    
    print("========================\n")

# This function is called when a WebSocket connection is closed
def websocket_end(flow: websocket.WebSocketMessage):
    print(f"=== WEBSOCKET CONNECTION CLOSED ===")
    print(f"Client to {flow.request.host} WebSocket connection closed")
    print("=============================\n")