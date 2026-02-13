# 🔐 Login Credentials

## Test User Account

**Username:** `testuser`  
**Password:** `password123`  
**Email:** `testuser@gmail.com`

---

## How to Login

### From Frontend:
1. Open: http://localhost:5173
2. Navigate to Login page
3. Enter credentials above
4. Click Login

### Test API Directly:
```bash
# Using curl
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"testuser\",\"password\":\"password123\"}"
```

### Using Browser (API Docs):
1. Open: http://localhost:8000/docs
2. Find `POST /api/auth/login`
3. Click "Try it out"
4. Enter:
   ```json
   {
     "username": "testuser",
     "password": "password123"
   }
   ```
5. Click "Execute"

---

## Create New User

### Via API:
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\":\"newuser\",
    \"email\":\"newuser@example.com\",
    \"password\":\"yourpassword\",
    \"full_name\":\"Your Name\"
  }"
```

### Via Frontend:
Navigate to Register page and fill in the form.

---

## Reset Password

If you forget the password, run:
```bash
cd backend
python scripts\reset_password.py
```

This will reset the testuser password back to `password123`.

---

## Troubleshooting

### "Incorrect username or password"
- ✅ Password has been reset to: `password123`
- ✅ Username is case-sensitive: use `testuser` (lowercase)
- ✅ Make sure backend server is running

### "Database error"
- Restart the backend server
- Check [DATABASE-FIX.md](DATABASE-FIX.md) for details

### Backend not responding
- Ensure backend is running on http://localhost:8000
- Check console for errors
- Restart using `start-backend.bat`

---

**✅ Your login should now work!** Use the credentials above.
