# 🐛 Debug Guide - Connection Issues

## ✅ Fixes Applied

### **1. Removed pygame.display.flip() from base_screen.py**
- Prevents double rendering (flickering)
- Each screen now calls flip() only once in their own draw()

### **2. Fixed Status Label Updates**
The label now updates properly:
- "Disconnected" → "Connecting..." → "Connected" 
- "Disconnected" when connection lost
- Updates in real-time in update() method

### **3. Fixed Connection Loss Issue**
**The Problem:** When starting the game, the multiplayer menu's `on_exit()` was disconnecting the client!

**The Fix:**
- Removed disconnect from `on_exit()` in multiplayer_menu.py
- Only disconnect when explicitly clicking "Disconnect" or "Back"
- Keep connection alive when switching to game screen

---

## 🧪 Testing Steps

### **Step 1: Test Connection**
```bash
# Terminal 1 - Server
cd server
python game_server.py
```

You should see:
```
============================================================
[STARTED] Game server listening on 0.0.0.0:50000
============================================================
```

### **Step 2: Test Client Connection**
```bash
# Terminal 2 - Client
python main.py
```

1. Click "Multiplayer"
2. **Check:** Label says "Disconnected" ✓
3. **Check:** Join/Host buttons are grayed out ✓
4. Click "Connect to Server"
5. **Check:** Label briefly shows "Connecting..." ✓
6. **Check:** Server terminal shows "[NEW CONNECTION]" ✓
7. **Check:** Label changes to "Connected" ✓
8. **Check:** Button changes to "Disconnect" ✓
9. **Check:** Join/Host buttons become enabled ✓

### **Step 3: Test Game Start**
1. Click "Host Game" or "Join Game"
2. **Check:** Game screen appears ✓
3. **Check:** Blue square visible ✓
4. **Check:** Server still shows connection active ✓
5. **Check:** No "Connection lost" messages ✓

### **Step 4: Test Movement**
1. Press W/A/S/D
2. **Check:** Blue square moves ✓
3. Open another client and repeat
4. **Check:** Both players see each other ✓

---

## 🔍 If Still Not Working

### **Issue: "Connection lost during game!"**

**Possible causes:**

#### **A. Server crashed or stopped**
Check server terminal - should show:
```
[NEW CONNECTION] Player 1 connected from ('127.0.0.1', 54321)
[ACTIVE CONNECTIONS] 1
```

If server shows error or disconnection, that's the issue.

#### **B. Client reference not passed correctly**
Add debug prints to check:

In `main.py`, add to `_start_multiplayer_game()`:
```python
def _start_multiplayer_game(self, client, is_host):
    print(f"[DEBUG] Starting game...")
    print(f"[DEBUG] Client object: {client}")
    print(f"[DEBUG] Client connected: {client.is_connected()}")
    # ... rest of code
```

#### **C. Network issue**
Test with explicit connection check:

In `game_screen.py`, add to `update()`:
```python
def update(self, dt):
    super().update(dt)
    
    # DEBUG
    if not self.client.is_connected():
        print(f"[DEBUG] Client not connected!")
        print(f"[DEBUG] Error: {self.client.get_error()}")
        self._exit_game()
        return
```

---

## 🔧 Quick Fixes to Try

### **Fix 1: Ensure Client is Passed Correctly**

Check that `multiplayer_menu.py` passes the SAME client instance:

```python
def _join_game(self):
    print(f"[DEBUG] Join - Client connected: {self.client.is_connected()}")
    if self.callbacks.get('start_game'):
        self.callbacks['start_game'](self.client, is_host=False)

def _host_game(self):
    print(f"[DEBUG] Host - Client connected: {self.client.is_connected()}")
    if self.callbacks.get('start_game'):
        self.callbacks['start_game'](self.client, is_host=True)
```

### **Fix 2: Check Socket Timeout**

In `game/multiplayer/client.py`, the socket might be timing out during gameplay.

Add to `send_input()`:
```python
def send_input(self, input_state):
    if not self.connected or not self.socket:
        print("[DEBUG] Cannot send - not connected")
        return False
    
    try:
        input_state["name"] = self.player_name
        data = pickle.dumps(input_state)
        self.socket.sendall(data)
        return True
    except Exception as e:
        print(f"[DEBUG] Send error: {e}")
        # ... rest
```

### **Fix 3: Server Receive Issue**

Check if server is properly receiving data. In `server/game_server.py`:

```python
# In handle_client function:
while True:
    data = conn.recv(1024)
    if not data:
        print(f"[DEBUG] No data received from Player {player_id}")
        break
    
    print(f"[DEBUG] Received from Player {player_id}: {len(data)} bytes")
    # ... rest
```

---

## 📋 Updated Files Checklist

Make sure you updated these files:

- [x] `gui/screens/base_screen.py` - Removed flip()
- [x] `gui/screens/multiplayer_menu.py` - Fixed connection handling
- [x] `main.py` - Fixed callbacks
- [ ] `game/multiplayer/client.py` - (should be fine, but check if issues persist)
- [ ] `server/game_server.py` - (should be fine, but check if issues persist)

---

## 🎯 Expected Console Output

### **Server:**
```
============================================================
[STARTED] Game server listening on 0.0.0.0:50000
============================================================
Waiting for connections...

[NEW CONNECTION] Player 1 connected from ('127.0.0.1', 54321)
[ACTIVE CONNECTIONS] 1
```

### **Client:**
```
Switched to screen: multiplayer
Attempting to connect to server...
Connecting to 127.0.0.1:50000 as Player
Connected to server at 127.0.0.1:50000
Connected successfully!
Receive thread started
Starting multiplayer game (host=True)...
Switched to screen: game
```

**NOT this:**
```
Connection lost during game!  ← BAD!
```

---

## 💡 Common Issues

### **Issue: Flickering screen**
✅ **Fixed** - Removed double flip()

### **Issue: Label not updating**
✅ **Fixed** - Added update() logic to check connection status

### **Issue: Connection lost when starting game**
✅ **Fixed** - Removed disconnect from on_exit()

### **Issue: Connection timeout**
**Solution:** Check server is running and accessible
```bash
# Test with telnet or netcat
telnet 127.0.0.1 50000
# or
nc -zv 127.0.0.1 50000
```

### **Issue: Multiple connections but not seeing each other**
**Check:** Server is broadcasting to all clients
**Check:** Both clients connected to SAME server

---

## 🚀 Next Debugging Steps

If still having issues, add these debug prints:

**1. In multiplayer_menu.py:**
```python
def _connect_to_server(self):
    # ... existing code ...
    print(f"[DEBUG] Client ID after connect: {id(self.client)}")
    print(f"[DEBUG] Connected: {self.client.is_connected()}")
```

**2. In main.py:**
```python
def _start_multiplayer_game(self, client, is_host):
    print(f"[DEBUG] Received client ID: {id(client)}")
    print(f"[DEBUG] Same as multiplayer menu? {id(client) == id(self.screens['multiplayer'].client)}")
```

**3. In game_screen.py:**
```python
def __init__(self, screen, config, client, is_host, back_callback):
    # ... existing code ...
    print(f"[DEBUG] GameScreen got client ID: {id(self.client)}")
    print(f"[DEBUG] Client connected: {self.client.is_connected()}")
```

This will help trace if the client object is being passed correctly!

---

Let me know what you see! 🔍
