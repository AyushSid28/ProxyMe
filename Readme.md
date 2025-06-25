Welcome to Ayush’s AI Assistant, a stylish, ChatGPT-inspired chatbot built with FastAPI (backend) and Node.js with EJS (frontend). This project allows users to chat in real-time, extract leads, and send notifications, all hosted on Render.


Setup:
 
 git clone 
 cd my-agentic-clone


1.Backend Setup:
  pip install -r requirements.txt

   OPENAI_API_KEY=sk-...
   PUSHOVER_TOKEN=...
   PUSHOVER_USER_KEY=...
   CORS_ORIGINS=http://localhost:3000
   USE_EVALUATOR=false


   Run the Fast API server:
      uvicorn main:app --reload  --port 8001
