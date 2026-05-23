import { useState, useEffect, useRef } from 'react';
import './App.css';

// --- Configuration ---
const POST_CHAT_WEBHOOK = "http://localhost:5678/webhook/voice-booking"; 
const GET_CALENDAR_WEBHOOK = "http://localhost:5678/webhook/calendar-week"; 

function App() {
  const [status, setStatus] = useState({ text: "● System Ready", color: "#10b981" });
  const [isRecording, setIsRecording] = useState(false);
  const [lang, setLang] = useState("en-US");
  const [textInput, setTextInput] = useState("");
  const [chatLog, setChatLog] = useState({ user: "", ai: "" });
  
  const [calendarData, setCalendarData] = useState(null);

  const recognitionRef = useRef(null);
  const currentWeekRef = useRef(null); // Safely tracks the current week for refreshing

  useEffect(() => {
    fetchCalendar();
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      
      recognitionRef.current.onresult = async (event) => {
        const transcript = event.results[0][0].transcript;
        setChatLog({ user: transcript, ai: "" });
        await processAIRequest(transcript);
      };

      recognitionRef.current.onerror = () => resetUI("● Microphone Error", "#ef4444");
      recognitionRef.current.onend = () => setIsRecording(false);
    }
  }, []);

  const fetchCalendar = async (startDateStr = null) => {
    try {
      let url = GET_CALENDAR_WEBHOOK;
      if (startDateStr) url += `?startDate=${startDateStr}`;
      
      const response = await fetch(url);
      const data = await response.json();
      setCalendarData(data);
      currentWeekRef.current = data.weekStartDateStr; // Save the active week
    } catch (error) {
      console.error("Failed to fetch calendar", error);
    }
  };

  const processAIRequest = async (text) => {
    setStatus({ text: "● Thinking...", color: "#f59e0b" });
    setIsRecording(true); 

    try {
      const response = await fetch(POST_CHAT_WEBHOOK, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });

      const data = await response.json();
      setStatus({ text: "● Replying...", color: "#8b5cf6" });
      setChatLog({ user: text, ai: data.reply });

      // Wait 2 seconds for Google Calendar to sync, then refresh the grid!
      setTimeout(() => {
        fetchCalendar(currentWeekRef.current);
      }, 2000);

      const utterance = new SpeechSynthesisUtterance(data.reply);
      utterance.lang = lang;
      utterance.onend = () => resetUI("● System Ready", "#10b981");
      window.speechSynthesis.speak(utterance);

    } catch (error) {
      resetUI("● Connection Failed", "#ef4444");
    }
  };

  const handleStartRecord = () => {
    if (recognitionRef.current) {
      recognitionRef.current.lang = lang;
      recognitionRef.current.start();
      setStatus({ text: "● Listening...", color: "#3b82f6" });
      setIsRecording(true);
    }
  };

  const handleStopRecord = () => {
    if (recognitionRef.current) recognitionRef.current.stop();
  };

  const handleTextSubmit = async () => {
    if (!textInput) return;
    setChatLog({ user: textInput, ai: "" });
    const textToSend = textInput;
    setTextInput('');
    await processAIRequest(textToSend);
  };

  const resetUI = (text, color) => {
    setStatus({ text, color });
    setIsRecording(false);
  };

  const handleSlotClick = (slotTime, dayDateStr) => {
    setTextInput(`Book an appointment on ${dayDateStr} at ${slotTime}`);
  };

  return (
    <div className="app-container">
      
      {/* LEFT PANEL: Chat and Controls */}
      <div className="left-panel">
        <div className={`avatar ${isRecording ? 'listening' : ''}`}>🤖</div>
        <h2>AI Assistant</h2>
        <div className="status" style={{ color: status.color }}>{status.text}</div>

        <div className="controls">
          <select value={lang} onChange={(e) => setLang(e.target.value)}>
            <option value="en-US">English</option>
            <option value="hi-IN">Hindi</option>
            <option value="ta-IN">Tamil</option>
          </select>
          
          {!isRecording ? (
            <button onClick={handleStartRecord}>🎙️ Hold to Speak</button>
          ) : (
            <button onClick={handleStopRecord} className="btn-stop">🛑 Stop & Send</button>
          )}
          
          <div className="divider">OR TYPE</div>
          
          <input 
            type="text" 
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            placeholder="Book a meeting at 3pm..."
            onKeyPress={(e) => e.key === 'Enter' && handleTextSubmit()}
          />
          <button onClick={handleTextSubmit}>Send Message</button>
        </div>

        {(chatLog.user || chatLog.ai) && (
          <div className="chat-bubble" style={{ display: 'block' }}>
            <strong>You:</strong> "{chatLog.user}"<br/><br/>
            {chatLog.ai && <span><strong>AI:</strong> "{chatLog.ai}"</span>}
          </div>
        )}
      </div>

      {/* RIGHT PANEL: The Calendar Grid */}
      <div className="right-panel">
        {calendarData ? (
          <div className="calendar-wrapper">
            <div className="week-navigation">
              <button onClick={() => {
                const currentStart = new Date(calendarData.weekStartDateStr);
                currentStart.setDate(currentStart.getDate() - 7);
                const prevWeekStr = currentStart.toISOString().split('T')[0];
                fetchCalendar(prevWeekStr);
              }}>⬅ Prev</button>

              <h4 style={{ margin: '0 10px', color: '#64748b', textAlign: 'center' }}>
                Week of {calendarData.weekStartDisplay}
              </h4>
              
              <button onClick={() => {
                const currentStart = new Date(calendarData.weekStartDateStr);
                currentStart.setDate(currentStart.getDate() + 7);
                const nextWeekStr = currentStart.toISOString().split('T')[0];
                fetchCalendar(nextWeekStr);
              }}>Next ➔</button>
            </div>

            {/* --- NEW: Filter to only show today and future dates --- */}
            {(() => {
              // 1. Get today's local date as "YYYY-MM-DD"
              const today = new Date();
              const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
              
              // 2. Filter out any days from the array that are older than today
              const availableDays = calendarData.days.filter(day => day.fullDate >= todayStr);

              // 3. Fallback message if the whole week is in the past (e.g. they clicked Prev)
              if (availableDays.length === 0) {
                return (
                  <div style={{ textAlign: 'center', marginTop: '40px', color: '#64748b', fontWeight: '600' }}>
                    Past dates are not available for booking.<br/><br/>
                    Please click Next ➔ to view upcoming slots.
                  </div>
                );
              }

              // 4. Render the valid days
              return availableDays.map((day, index) => (
                <div key={index} className="day-row">
                  <div className="day-title">{day.dayName}, {day.displayDate}</div>
                  <div className="slots-grid">
                    {day.slots.map((slot, sIdx) => (
                      <div 
                        key={sIdx} 
                        className={`slot ${slot.status}`}
                        onClick={() => slot.status === 'free' && handleSlotClick(slot.time, day.fullDate)}
                      >
                        {slot.time}
                      </div>
                    ))}
                  </div>
                </div>
              ));
            })()}
            
          </div>
        ) : (
            <div style={{ color: '#64748b', marginTop: '50px' }}>Loading Calendar...</div>
        )}
      </div>
      
    </div>
  );
}

export default App;