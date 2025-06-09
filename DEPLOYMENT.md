# ASRS Dashboard Deployment Guide

## Deploying to Render (Free)

### Prerequisites
- GitHub account
- Your code pushed to GitHub repository

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit for deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/asrs-dashboard.git
git push -u origin main
```

### Step 2: Deploy to Render
1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `asrs-dashboard`
   - **Environment**: `Node`
   - **Build Command**: `npm install`
   - **Start Command**: `npm start`
   - **Plan**: `Free`

### Step 3: Environment Variables
Add these in Render dashboard under "Environment":
- `NODE_ENV` = `production`
- `PORT` = `3000`

### Step 4: Install Python Dependencies
In your Render dashboard, go to the "Shell" tab and run:
```bash
pip install -r requirements.txt
```

### Deployment Notes
- First deployment takes 5-10 minutes
- Free tier sleeps after 15 minutes of inactivity
- Large CSV file (21MB) is included but may slow initial load

### Alternative: Railway Deployment
If Render doesn't work, try Railway.app (also has free tier) 