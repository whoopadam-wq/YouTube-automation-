# 🎨 Web Dashboard Quick Start Guide

## 🚀 Launch the Dashboard

### Option 1: Use Startup Script (Recommended)

**Linux/Mac:**
```bash
./start_dashboard.sh
```

**Windows:**
```bash
start_dashboard.bat
```

### Option 2: Manual Start
```bash
python dashboard/app.py
```

The dashboard will start on **http://localhost:5000**

---

## 📊 Dashboard Overview

### Main Dashboard (Home)
**URL:** http://localhost:5000

**Features:**
- **Live Stats Cards**
  - Active Channels
  - Completed Videos Today
  - Spent Today
  - Videos In Progress

- **Interactive Charts**
  - Cost Overview (Bar Chart)
  - Generation Status (Pie Chart)

- **Channels Table**
  - Real-time budget usage
  - Visual progress bars
  - Quick actions

- **System Status**
  - Budget caps
  - Monthly spending
  - Active tasks

- **Alerts**
  - Automatic warnings at 80% budget
  - Critical alerts at 90%

**Auto-Refresh:** Every 5 seconds

---

### Channels Page
**URL:** http://localhost:5000/channels

**Features:**
- Beautiful card-based layout
- Per-channel information:
  - Budget usage with progress bars
  - Long-form/shorts status
  - Visual style indicators
  - Niche badges

**Click "View Details" for:**
- Full channel configuration
- Cost breakdown (7 days)
- Recent videos
- Base prompt and tone modifiers

**Auto-Refresh:** Every 15 seconds

---

### Generate Page
**URL:** http://localhost:5000/generate

**Features:**
- **Manual Generation Controls**
  - Long-Form Videos
    - Select channel
    - See cost estimate
    - One-click generation

  - Shorts
    - Select channel
    - Choose number of shorts (1-10)
    - See cost estimate
    - Generate multiple shorts

- **Real-Time Progress**
  - Shows generation status
  - Completion notifications

- **Recent Generations Table**
  - Last 10 videos
  - Status tracking
  - Quick view details

**How to Generate:**
1. Select a channel from dropdown
2. Review estimated cost
3. Click "Generate" button
4. Monitor progress in real-time
5. Get success notification with video ID

**Auto-Refresh:** Every 10 seconds (recent table)

---

### Costs Page
**URL:** http://localhost:5000/costs

**Features:**
- **Budget Overview Cards**
  - Today's spend
  - This month's total
  - Remaining budget

- **Per-Channel Costs Table**
  - Daily spending
  - Monthly totals
  - Budget limits
  - Usage percentage with color-coded progress

- **Cost Breakdown Chart**
  - Pie chart showing:
    - Text generation
    - Image generation
    - Video generation
    - Voice synthesis
    - Character creation

**Auto-Refresh:** Every 10 seconds

---

### Schedule Page
**URL:** http://localhost:5000/schedule

**Features:**
- View automated schedules per channel
- Long-form video schedules
- Shorts schedules with frequency
- Timezone information

---

### History Page
**URL:** http://localhost:5000/history

**Features:**
- All generated videos across channels
- Filter by channel dropdown
- Sortable table:
  - Video ID
  - Channel
  - Type (long_form/short_form)
  - Status
  - Title
  - Creation date

**Status Indicators:**
- ✅ Green: Uploaded
- ⚠️ Yellow: Pending Upload
- ❌ Red: Failed
- ℹ️ Blue: In Progress

**Auto-Refresh:** Every 10 seconds

---

## 🎯 Common Workflows

### Workflow 1: Monitor System Health
1. Open dashboard home
2. Check stat cards for overview
3. Review alerts (if any)
4. Check budget usage per channel

### Workflow 2: Generate Content
1. Go to Generate page
2. Select channel
3. Choose long-form or shorts
4. Review cost estimate
5. Click Generate
6. Monitor progress
7. Check History for results

### Workflow 3: Track Costs
1. Go to Costs page
2. Review today's spending
3. Check per-channel breakdown
4. View cost distribution in pie chart
5. Ensure within budget limits

### Workflow 4: Manage Channels
1. Go to Channels page
2. View all active channels
3. Click "View Details" for any channel
4. Review:
   - Cost breakdown
   - Recent videos
   - Configuration
   - Budget usage

---

## 🎨 Design Features

### Color Coding
- **Blue/Purple Gradients** - Primary actions and headers
- **Green** - Success, completed, healthy status
- **Yellow/Orange** - Warnings, pending status
- **Red** - Errors, failed, over-budget
- **Dark Theme** - Easy on the eyes

### Visual Elements
- **Glassmorphism** - Translucent cards with backdrop blur
- **Gradients** - Smooth color transitions
- **Animations** - Hover effects and transitions
- **Progress Bars** - Real-time budget usage
- **Charts** - Interactive Chart.js visualizations

### Responsive Design
- Works on desktop (1920px+)
- Works on tablets (768px+)
- Works on mobile (320px+)

---

## 🔧 Troubleshooting

### Dashboard Won't Start
```bash
# Install Flask dependencies
pip install flask flask-cors

# Or reinstall all dependencies
pip install -r requirements.txt
```

### Port 5000 Already in Use
Edit `dashboard/app.py` and change:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Charts Not Loading
- Check browser console for errors
- Ensure Chart.js CDN is accessible
- Try hard refresh (Ctrl+Shift+R)

### Data Not Updating
- Check if backend APIs are working
- Try manual refresh (F5)
- Check browser network tab for API errors

---

## 📱 Mobile Access

Access the dashboard from other devices on your network:

1. Find your computer's IP address:
   ```bash
   # Linux/Mac
   ifconfig | grep inet

   # Windows
   ipconfig
   ```

2. Open browser on mobile/tablet:
   ```
   http://<your-ip-address>:5000
   ```

---

## 🚀 Production Deployment

For production use with Gunicorn:

```bash
# Install Gunicorn
pip install gunicorn

# Run dashboard
gunicorn -w 4 -b 0.0.0.0:5000 dashboard.app:app
```

For public access, use a reverse proxy (nginx) or cloud platform (Heroku, AWS, etc.)

---

## 💡 Tips

1. **Keep dashboard open** - It auto-refreshes, so you can monitor in real-time
2. **Use filters** - On history page, filter by channel for focused view
3. **Check alerts** - Dashboard home shows budget warnings automatically
4. **Generate during low-cost times** - Monitor costs page before generation
5. **Review details** - Click channel cards for full configuration info

---

## 🎓 Next Steps

1. ✅ Launch dashboard
2. ✅ Review system status
3. ✅ Check channel configurations
4. ✅ Try manual generation
5. ✅ Monitor costs
6. ✅ Review generation history

**Enjoy your beautiful automation dashboard!** 🚀
