# ♻️ Prakrit – AI-Powered Smart Recycling Platform

Prakrit is an AI-enabled digital recycling platform designed to simplify waste identification, pricing, and pickup while encouraging sustainable behavior through rewards and environmental impact insights.

---

## 🚀 Overview

Prakrit helps users:
- Identify recyclable waste using AI
- Get an estimated fair value instantly
- Automatically connect with nearby recyclers
- Earn rewards and track environmental impact

The platform bridges the gap between households and recyclers using automation, AI/ML, and a clean user experience.

---

## ❓ Problem Statement

Recyclable waste often goes unmanaged due to:
- Lack of clarity on waste type and value  
- Manual negotiation and inconsistent pricing  
- Unstructured access to recyclers  
- Low motivation for users to recycle regularly  

These challenges result in recyclable materials ending up in landfills instead of being reused.

---

## 💡 Solution – How Prakrit Works

1. User uploads an image of waste through the app  
2. AI identifies the waste type and confidence score  
3. System estimates a price range  
4. Nearest recycler is automatically assigned  
5. Pickup is scheduled and completed  
6. User earns rewards and receives environmental impact feedback  

---

## 🎯 Target Audience

- Urban households and working professionals  
- Local recyclers and scrap collectors  
- Institutions and organizations focused on sustainability  

---

## 🧠 Core AI-Driven Features

### 1. AI Waste Identification
- Identifies waste type (Plastic, Paper, Metal, E-waste)
- Returns confidence score for accuracy

**Implementation**
- MobileNetV2 (Transfer Learning)
- Exported `.h5` model
- Served via FastAPI / Flask `/predict` endpoint

---

### 2. Basic Pricing Engine
- Suggests estimated price range
- Based on material type and confidence score

**Implementation**
- Rule-based pricing logic
- Confidence multiplier in backend

---

### 3. Auto Recycler Assignment
- Automatically assigns nearest recycler

**Implementation**
- Latitude–Longitude coordinates
- Distance calculation using Haversine formula

---

### 4. GenAI Communication Layer
- Converts technical system outputs into simple explanations

**Implementation**
- LLM-based prompts (Gemini / GPT)
- Integrated into app responses or chatbot UI

---

### 5. CO₂ & Environmental Impact Summary
- Displays carbon and environmental savings from recycling

**Implementation**
- Predefined CO₂ constants per material
- Basic formula-based computation

---

### 6. Rewards System
- Users earn points for confirmed pickups
- Points can be redeemed, withdrawn, or donated

**Implementation**
- Backend-based point counter
- Updated after pickup confirmation

---

## 🧱 Tech Stack

### Frontend
- React

### Backend
- Spring Boot

### Mobile App
- Kotlin (Android)

### AI / ML
- Deep Learning (Computer Vision)
- Rule-based ML
- Generative AI (NLP)

---

## 📱 Application Structure

### Customer App
- Home
- Upload
- Pickups
- Wallet
- Profile (popup menu)

### Admin Panel
- Dashboard
- Users
- Recyclers
- Pickups
- Transactions

---

## 🌱 Why Prakrit Stands Out

- Eliminates manual waste negotiation  
- Builds trust with AI confidence scoring  
- Improves recycler efficiency through automation  
- Encourages long-term sustainable habits  
- Practical, implementable AI/ML usage  

---

## 📌 Project Status

This repository represents an MVP-focused implementation suitable for:
- Hackathons
- Academic projects
- Early-stage startup prototypes

---

## 📄 License

This project is currently for educational and prototype purposes.

---

## 🙌 Acknowledgements

Inspired by real-world waste management challenges and sustainability goals, Prakrit aims to make recycling simple, transparent, and rewarding.
