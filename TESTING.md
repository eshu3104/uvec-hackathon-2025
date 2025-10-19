# 🧪 Testing Guide for Party Room Backend

This guide explains how to test the room management functionality.

## Test Files

- `tests/test_room_management.py` - Comprehensive unit tests
- `run_tests.py` - Test runner script
- `manual_test.py` - Manual API testing script

## Running Tests

### 1. Unit Tests (Automated)

Run all room management tests:
```bash
python3 run_tests.py --room-only
```

Run all tests:
```bash
python3 run_tests.py --all
```

### 2. Manual API Tests

Start your Flask server:
```bash
python3 run.py
```

In another terminal, run the manual test script:
```bash
python3 manual_test.py
```

## Test Coverage

### ✅ Room Management Tests

1. **Create Room**
   - ✅ Successful room creation with Spotify auth
   - ✅ Authentication required (401 without auth)
   - ✅ Spotify playlist creation
   - ✅ Host added as first participant

2. **Join Room**
   - ✅ Successful room joining
   - ✅ Room not found (404)
   - ✅ Inactive room (400)
   - ✅ Case insensitive room codes
   - ✅ Multiple participants

3. **Room Status**
   - ✅ Get room status and participants
   - ✅ Room not found (404)

4. **Leave Room**
   - ✅ Successful room leaving
   - ✅ Missing participant_id (400)
   - ✅ Participant not found (404)

5. **End Room**
   - ✅ Host successfully ends room
   - ✅ Authentication required (401)
   - ✅ Only host can end room (403)
   - ✅ Room status changed to 'ended'
   - ✅ Participants cleared

6. **Error Handling**
   - ✅ Invalid room codes
   - ✅ Missing authentication
   - ✅ Authorization failures
   - ✅ Malformed requests

7. **Edge Cases**
   - ✅ Room code uniqueness
   - ✅ Multiple rooms isolation
   - ✅ Case insensitive operations
   - ✅ Token refresh handling

### 🎵 Spotify Integration Tests

1. **Authentication Flow**
   - ✅ Spotify login redirect
   - ✅ OAuth callback handling
   - ✅ Token refresh
   - ✅ Session management

2. **Data Endpoints**
   - ✅ User profile retrieval
   - ✅ Playlist creation
   - ✅ Top tracks
   - ✅ Recently played
   - ✅ User playlists

## Manual Testing Steps

### 1. Test Without Authentication

```bash
# Start server
python3 run.py

# Run manual tests (will show auth errors)
python3 manual_test.py
```

### 2. Test With Spotify Authentication

1. **Authenticate with Spotify:**
   ```
   http://localhost:5000/api/spotify/login
   ```

2. **Run manual tests:**
   ```bash
   python3 manual_test.py
   ```

3. **Test room creation:**
   ```bash
   curl -X POST http://localhost:5000/api/create-room
   ```

4. **Test room joining:**
   ```bash
   curl -X POST http://localhost:5000/api/join-room/ABC123
   ```

## Expected Test Results

### Unit Tests
- **Total Tests**: 20+ test cases
- **Coverage**: All endpoints and error cases
- **Mocking**: Spotify API calls mocked for reliability

### Manual Tests
- **Authentication Flow**: Spotify OAuth integration
- **Room Lifecycle**: Create → Join → Leave → End
- **Error Handling**: Invalid requests and edge cases
- **Real API Calls**: Actual Spotify integration

## Test Data

### Room Structure
```json
{
  "code": "ABC123",
  "host_user_id": "spotify_user_id",
  "host_display_name": "John Doe",
  "playlist_id": "playlist_spotify_id",
  "playlist_url": "https://open.spotify.com/playlist/...",
  "created_at": "2025-01-27T10:30:00Z",
  "status": "active",
  "participant_count": 3
}
```

### Participant Structure
```json
{
  "user_id": "spotify_user_id_or_guest_1",
  "display_name": "John Doe or Guest 1",
  "joined_at": "2025-01-27T10:30:00Z",
  "is_host": true
}
```

## Troubleshooting

### Common Issues

1. **"Not authenticated with Spotify"**
   - Solution: Go to `/api/spotify/login` first

2. **"Room not found"**
   - Solution: Create room first or check room code

3. **"Only the host can end the room"**
   - Solution: Use the same Spotify account that created the room

4. **Connection refused**
   - Solution: Make sure Flask server is running on port 5000

### Debug Mode

Enable Flask debug mode for detailed error messages:
```python
# In run.py
app.run(debug=True, host='0.0.0.0', port=5000)
```

## Performance Testing

For load testing, you can use tools like:
- `ab` (Apache Bench)
- `wrk`
- `curl` with loops

Example:
```bash
# Test room creation under load
for i in {1..10}; do
  curl -X POST http://localhost:5000/api/create-room &
done
wait
```

## Continuous Integration

To run tests in CI/CD:
```bash
# Install dependencies
pip3 install -r requirements.txt

# Run tests
python3 run_tests.py --all

# Check exit code
echo $?  # Should be 0 for success
```
