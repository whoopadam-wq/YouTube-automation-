# ⚡ 5-Minute Cloud Deployment

Deploy your dashboard to get a **public HTTPS URL** in 5 minutes!

## 🚀 Steps

### 1. Sign Up (30 seconds)
- Go to https://render.com
- Click "Get Started"
- Sign up with GitHub

### 2. Create Service (1 minute)
- Dashboard → "New +" → "Web Service"
- Select this repository: `YouTube-automation-`
- Branch: `claude/ai-video-automation-system-atkMj`
- Render auto-detects settings ✅

### 3. Add API Keys (2 minutes)
Add these as environment variables:
```
ANTHROPIC_API_KEY = sk-ant-your-key
OPENAI_API_KEY = sk-your-key
REPLICATE_API_TOKEN = r8-your-token
ELEVENLABS_API_KEY = your-key
```

### 4. Add Persistent Disk (1 minute)
- Scroll to "Disk" section
- Click "Add Disk"
- Name: `data`
- Mount: `/opt/render/project/src/data`
- Size: `1 GB`

### 5. Deploy! (30 seconds)
- Click "Create Web Service"
- Wait 3-5 minutes for deployment
- Get your URL: `https://your-app.onrender.com`

## ✅ Done!

Your dashboard is now:
- Publicly accessible
- HTTPS secure
- Auto-updating from GitHub
- Free forever (on free tier)

## 📖 Need Help?

See full guide: [DEPLOYMENT.md](DEPLOYMENT.md)

## 🎯 What's Next?

1. Open your public URL
2. Check system status
3. Try generating content
4. Monitor from anywhere!

**That's it!** 🎉
