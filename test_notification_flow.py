#!/usr/bin/env python3
"""
Test script to verify the WebSocket notification system is working correctly.
This script will:
1. Create test users
2. Create a test painting
3. Simulate rating and commenting to trigger notifications
4. Verify notifications are sent via WebSocket
"""

import asyncio
import json
import websockets
import requests
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

class NotificationTester:
    def __init__(self):
        self.tokens = {}
        self.users = {}
        self.painting_id = None
        self.comment_id = None

    def create_user(self, username, email, password, full_name):
        """Create a new user and return the access token"""
        user_data = {
            "username": username,
            "email": email,
            "password": password,
            "full_name": full_name
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        if response.status_code == 201:
            print(f"✅ User {username} created successfully")
        elif response.status_code == 400 and "already registered" in response.text:
            print(f"ℹ️  User {username} already exists")
        else:
            print(f"❌ Failed to create user {username}: {response.text}")
            return None
            
        # Always try to login (whether user was just created or already existed)
        login_data = {"username": username, "password": password}
        login_response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            self.tokens[username] = token
            
            # Get user info
            headers = {"Authorization": f"Bearer {token}"}
            user_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            if user_response.status_code == 200:
                self.users[username] = user_response.json()
                print(f"✅ User {username} logged in successfully")
                return token
            else:
                print(f"❌ Failed to get user info for {username}: {user_response.text}")
        else:
            print(f"❌ Failed to login user {username}: {login_response.text}")
        
        return None

    def create_painting(self, token, title, description):
        """Create a test painting"""
        headers = {"Authorization": f"Bearer {token}"}
        
        # First, get available categories
        categories_response = requests.get(f"{BASE_URL}/categories/", headers=headers)
        if categories_response.status_code != 200:
            print(f"❌ Failed to get categories: {categories_response.text}")
            return None
            
        categories = categories_response.json()
        if not categories:
            print("❌ No categories available")
            return None
            
        category_id = categories[0]["id"]
        
        painting_data = {
            "title": title,
            "description": description,
            "category_id": category_id,
            "price": 100.0
        }
        
        response = requests.post(f"{BASE_URL}/paintings/", json=painting_data, headers=headers)
        if response.status_code == 201:
            painting = response.json()
            self.painting_id = painting["id"]
            print(f"✅ Painting '{title}' created with ID: {self.painting_id}")
            return painting
        else:
            print(f"❌ Failed to create painting: {response.text}")
            return None

    async def listen_for_notifications(self, username, token, duration=30):
        """Listen for WebSocket notifications for a user"""
        user_id = self.users[username]["id"]
        ws_url = f"{WS_URL}/ws/{user_id}?token={token}"
        
        print(f"🔗 Connecting WebSocket for {username} (ID: {user_id})")
        
        try:
            async with websockets.connect(ws_url) as websocket:
                print(f"✅ WebSocket connected for {username}")
                
                # Listen for notifications
                start_time = time.time()
                while time.time() - start_time < duration:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(message)
                        
                        if data.get("type") == "notification":
                            notification = data.get("data", {})
                            print(f"🔔 {username} received notification:")
                            print(f"   Type: {notification.get('type')}")
                            print(f"   Message: {notification.get('message')}")
                            print(f"   From: {notification.get('sender', {}).get('username')}")
                            print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
                            print()
                        elif data.get("type") == "unread_count":
                            count = data.get("data", {}).get("count", 0)
                            print(f"📊 {username} unread count updated: {count}")
                        else:
                            print(f"📩 {username} received message: {data}")
                            
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        print(f"❌ Error receiving message for {username}: {e}")
                        break
                        
        except Exception as e:
            print(f"❌ WebSocket connection failed for {username}: {e}")

    def rate_painting(self, token, painting_id, rating):
        """Rate a painting"""
        headers = {"Authorization": f"Bearer {token}"}
        rating_data = {"painting_id": painting_id, "rating": rating}
        
        response = requests.post(f"{BASE_URL}/ratings/", json=rating_data, headers=headers)
        if response.status_code == 201:
            print(f"✅ Painting rated with {rating} stars")
            return response.json()
        else:
            print(f"❌ Failed to rate painting: {response.text}")
            return None

    def comment_on_painting(self, token, painting_id, content):
        """Comment on a painting"""
        headers = {"Authorization": f"Bearer {token}"}
        comment_data = {"painting_id": painting_id, "content": content}
        
        response = requests.post(f"{BASE_URL}/comments/", json=comment_data, headers=headers)
        if response.status_code == 201:
            comment = response.json()
            self.comment_id = comment["id"]
            print(f"✅ Comment posted: '{content}'")
            return comment
        else:
            print(f"❌ Failed to post comment: {response.text}")
            return None

    def reply_to_comment(self, token, comment_id, content):
        """Reply to a comment"""
        headers = {"Authorization": f"Bearer {token}"}
        reply_data = {"parent_id": comment_id, "content": content}
        
        response = requests.post(f"{BASE_URL}/comments/", json=reply_data, headers=headers)
        if response.status_code == 201:
            print(f"✅ Reply posted: '{content}'")
            return response.json()
        else:
            print(f"❌ Failed to post reply: {response.text}")
            return None

    async def run_test(self):
        """Run the complete notification test"""
        print("🚀 Starting WebSocket Notification Test")
        print("=" * 50)
        
        # Step 1: Create test users
        print("\n📝 Step 1: Creating test users...")
        artist_token = self.create_user("test_artist", "artist@test.com", "password123", "Test Artist")
        enthusiast_token = self.create_user("test_enthusiast", "enthusiast@test.com", "password123", "Test Enthusiast")
        
        if not artist_token or not enthusiast_token:
            print("❌ Failed to create users. Exiting.")
            return
            
        # Step 2: Create a test painting
        print("\n🎨 Step 2: Creating test painting...")
        painting = self.create_painting(artist_token, "Test Painting for Notifications", "A beautiful test painting")
        
        if not painting:
            print("❌ Failed to create painting. Exiting.")
            return
            
        # Step 3: Set up WebSocket listeners
        print("\n🔗 Step 3: Setting up WebSocket connections...")
        
        # Create tasks to listen for notifications
        artist_listener = asyncio.create_task(
            self.listen_for_notifications("test_artist", artist_token, 20)
        )
        enthusiast_listener = asyncio.create_task(
            self.listen_for_notifications("test_enthusiast", enthusiast_token, 20)
        )
        
        # Give WebSocket connections time to establish
        await asyncio.sleep(2)
        
        # Step 4: Test rating notification
        print("\n⭐ Step 4: Testing rating notification...")
        print("Enthusiast will rate the artist's painting...")
        await asyncio.sleep(1)
        
        rating = self.rate_painting(enthusiast_token, self.painting_id, 5)
        if rating:
            print("✅ Rating submitted - artist should receive notification")
            await asyncio.sleep(3)
        
        # Step 5: Test comment notification
        print("\n💬 Step 5: Testing comment notification...")
        print("Enthusiast will comment on the artist's painting...")
        await asyncio.sleep(1)
        
        comment = self.comment_on_painting(enthusiast_token, self.painting_id, "This is a beautiful painting!")
        if comment:
            print("✅ Comment submitted - artist should receive notification")
            await asyncio.sleep(3)
        
        # Step 6: Test reply notification
        print("\n↩️  Step 6: Testing reply notification...")
        print("Artist will reply to the enthusiast's comment...")
        await asyncio.sleep(1)
        
        if self.comment_id:
            reply = self.reply_to_comment(artist_token, self.comment_id, "Thank you so much for your kind words!")
            if reply:
                print("✅ Reply submitted - enthusiast should receive notification")
                await asyncio.sleep(3)
        
        # Step 7: Wait for all notifications to be processed
        print("\n⏳ Step 7: Waiting for notifications to be processed...")
        await asyncio.sleep(5)
        
        # Cancel the listeners
        artist_listener.cancel()
        enthusiast_listener.cancel()
        
        try:
            await artist_listener
        except asyncio.CancelledError:
            pass
            
        try:
            await enthusiast_listener
        except asyncio.CancelledError:
            pass
        
        print("\n✅ Test completed!")
        print("=" * 50)

async def main():
    tester = NotificationTester()
    await tester.run_test()

if __name__ == "__main__":
    print("WebSocket Notification System Test")
    print("This script will test the real-time notification functionality")
    print("Make sure both backend and frontend servers are running")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
