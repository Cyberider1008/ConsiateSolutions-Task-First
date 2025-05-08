import json
from channels.generic.websocket import WebsocketConsumer

class OrderConsumer(WebsocketConsumer):
    groups = ['products']    
    def connect(self):
        self.accept()
        self.send(text_data=json.dumps({
            'type': 'websocket.connect',
            'message': "Connected......!"
        }))

    def receive(self, event=None, text_data=None):
        self.send(text_data=json.dumps({
            'type': 'websocket.message',
            'message': text_data
        }))
        
    def order_placed(self, event):
        self.send(text_data=json.dumps({
            'type': 'websocket.message',
            'message': event['message']
        }))
    