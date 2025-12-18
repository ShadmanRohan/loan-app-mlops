#!/usr/bin/env python3
"""
GitHub Webhook Server for Auto-Deployment
Listens for GitHub push events and triggers deployment
"""

import os
import json
import hmac
import hashlib
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Configuration
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your-webhook-secret-here')
DEPLOY_SCRIPT = '/home/rohan/Desktop/MLOps/ml-orchestration/scripts/deploy.sh'
PORT = 8080

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Only handle GitHub webhooks
        if not self.path.startswith('/github-webhook'):
            self.send_response(404)
            self.end_headers()
            return

        # Read the request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        # Verify GitHub signature
        if not self.verify_signature(body):
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'Unauthorized')
            return

        # Parse the payload
        try:
            payload = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid JSON')
            return

        # Only deploy on push to main branch
        if (payload.get('ref') == 'refs/heads/main' and 
            payload.get('repository', {}).get('full_name') == 'your-username/your-repo'):
            
            print(f"🚀 Deploying commit: {payload.get('head_commit', {}).get('id', 'unknown')}")
            
            # Run deployment script
            try:
                result = subprocess.run(
                    ['bash', DEPLOY_SCRIPT],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    print("✅ Deployment successful")
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'Deployment successful')
                else:
                    print(f"❌ Deployment failed: {result.stderr}")
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(f'Deployment failed: {result.stderr}'.encode())
                    
            except subprocess.TimeoutExpired:
                print("⏰ Deployment timeout")
                self.send_response(504)
                self.end_headers()
                self.wfile.write(b'Deployment timeout')
            except Exception as e:
                print(f"💥 Deployment error: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f'Deployment error: {str(e)}'.encode())
        else:
            # Not a main branch push, ignore
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Ignored (not main branch)')

    def verify_signature(self, body):
        """Verify GitHub webhook signature"""
        signature = self.headers.get('X-Hub-Signature-256', '')
        if not signature.startswith('sha256='):
            return False
        
        expected = hmac.new(
            WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f'sha256={expected}', signature)

    def log_message(self, format, *args):
        """Override to reduce log noise"""
        pass

if __name__ == '__main__':
    print(f"🔗 Starting webhook server on port {PORT}")
    print(f"📝 Listening for GitHub webhooks at: http://localhost:{PORT}/github-webhook")
    print(f"🔐 Using webhook secret: {WEBHOOK_SECRET[:10]}...")
    
    server = HTTPServer(('', PORT), WebhookHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Webhook server stopped")
        server.shutdown()







