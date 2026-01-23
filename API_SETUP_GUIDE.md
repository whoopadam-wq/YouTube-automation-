# API Setup Guide - Required for Real Data

This system needs API keys to access real YouTube data and discover trends. Here's how to set them up:

---

## 🔑 Required API Keys

### 1. **YouTube Data API v3** (REQUIRED)
**What it does:** Fetches real channel data, subscriber counts, video stats, analytics

**How to get it:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project (or select existing)
3. Click **"Enable APIs and Services"**
4. Search for **"YouTube Data API v3"** and enable it
5. Go to **Credentials** > **Create Credentials** > **API Key**
6. Copy your API key

**Where to add it in Render:**
- Dashboard > Your Service > Environment
- Add variable: `YOUTUBE_DATA_API_KEY`
- Paste your key
- Save and redeploy

**Cost:** FREE (10,000 requests/day)

---

### 2. **Serper API** (Optional but recommended)
**What it does:** Discovers real trending topics by scraping Google search results

**How to get it:**
1. Go to [serper.dev](https://serper.dev/)
2. Sign up for free account
3. Get your API key from dashboard

**Where to add it:**
- Render Dashboard > Environment
- Add variable: `SERPER_API_KEY`
- Paste your key

**Cost:** FREE tier: 2,500 searches/month

---

### 3. **Anthropic API** (Optional - for advanced features)
**What it does:** Powers script generation, analytics, and AI reasoning

**How to get it:**
1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Sign up and get API key
3. Add credits to your account

**Where to add it:**
- Render Dashboard > Environment
- Add variable: `ANTHROPIC_API_KEY`
- Paste your key

**Cost:** Pay-as-you-go (~$3 per 1M input tokens)

---

## 📋 Quick Setup Checklist

- [ ] Get YouTube Data API key (REQUIRED)
- [ ] Enable YouTube Data API v3 in Google Cloud
- [ ] Add `YOUTUBE_DATA_API_KEY` to Render environment
- [ ] Get Serper API key (for trend discovery)
- [ ] Add `SERPER_API_KEY` to Render environment
- [ ] Redeploy your Render service
- [ ] Test by pasting your YouTube channel URL

---

## 🚨 What Happens Without API Keys?

### Without YouTube Data API Key:
❌ **Channel Integration fails** - Can't connect to your channel
❌ **No real subscriber counts** - Can't fetch channel stats
❌ **No video analytics** - Can't analyze your content
❌ **System shows error message** - Won't work at all

### Without Serper API Key:
⚠️ **Ideas Discovery limited** - Can't find trending topics
⚠️ **Trend monitoring disabled** - No real-time viral alerts
✅ **Everything else works** - Channel integration still functional

### Without Anthropic API Key:
⚠️ **Script generation basic** - Uses fallback methods
⚠️ **Analytics simplified** - Less intelligent insights
✅ **Production still works** - Videos can still be made

---

## 🔧 How to Add Environment Variables in Render

1. Go to your Render dashboard
2. Select your service: `youtube-automation-2`
3. Click **"Environment"** in left sidebar
4. Click **"Add Environment Variable"**
5. Add each key:
   ```
   Key: YOUTUBE_DATA_API_KEY
   Value: [paste your key]
   ```
6. Click **"Save Changes"**
7. Service will automatically redeploy

---

## ✅ Testing Your Setup

After adding API keys and redeploying:

1. Visit your Render URL
2. Paste your YouTube channel URL in the input box
3. Click "Connect Channel"
4. You should see:
   - ✅ Real channel name
   - ✅ Actual subscriber count
   - ✅ Correct number of videos
   - ✅ Real niche detected

5. Click "Discover Ideas"
6. You should see:
   - ✅ Real trending topics from Google
   - ✅ Actual search results
   - ✅ Current viral content

---

## 💰 Cost Breakdown

| API | Free Tier | Paid Cost |
|-----|-----------|-----------|
| YouTube Data API | 10,000 requests/day | Free |
| Serper API | 2,500 searches/month | $50/month for 10K |
| Anthropic API | $5 free credit | ~$3-15 per 1M tokens |

**For typical usage:**
- Analyzing 1 channel: ~50 API calls (FREE)
- Discovering 10 ideas: ~10 searches (FREE)
- Generating 1 script: ~$0.05-0.20

**Most users can run on completely FREE tier!** 🎉

---

## 🆘 Troubleshooting

### "Channel integration failed"
- ✅ Check `YOUTUBE_DATA_API_KEY` is set correctly
- ✅ Make sure YouTube Data API v3 is enabled in Google Cloud
- ✅ Verify API key has no restrictions blocking YouTube API
- ✅ Redeploy after adding the key

### "No trending ideas found"
- ✅ Check `SERPER_API_KEY` is set
- ✅ Verify you have remaining free searches
- ✅ Try again in a few minutes

### "Learning system not starting"
- ✅ Make sure channel is connected first
- ✅ Check logs in Render dashboard for errors
- ✅ Verify all required API keys are present

---

## 📚 Additional Resources

- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)
- [Serper API Docs](https://serper.dev/docs)
- [Anthropic API Docs](https://docs.anthropic.com/)
- [Render Environment Variables Guide](https://render.com/docs/environment-variables)

---

## 🎯 Next Steps

1. **Get your YouTube Data API key** (5 minutes)
2. **Add it to Render environment** (2 minutes)
3. **Redeploy** (automatic)
4. **Connect your channel** - It will now work with real data!
5. **(Optional)** Add Serper API key for trend discovery
6. **(Optional)** Add Anthropic API key for advanced AI features

**Total setup time: ~10 minutes for free tier** ⏱️

---

*Need help? The system will show clear error messages telling you exactly what's missing and how to fix it.*
