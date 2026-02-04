# <a name="_c2vlcrpft0n0"></a>**Project 4: Build a Conversational Voice AI Agent**
## <a name="_hk4dv3ijuunl"></a>**Overview**
Build an AI-powered voice agent that handles inbound calls for a **restaurant reservation system**. The agent should be able to greet callers, check table availability, book reservations, and confirm details—all through natural conversation. This project simulates exactly what our customers want to build, whether they're using Plivo CX or rolling their own solution with our APIs.

**Estimated Time:** 1-2 days

-----
## <a name="_ax9vk4olv9n2"></a>**What You're Building**
A caller dials in and has a conversation like this:

**Agent:** "Hi, thanks for calling Mario's Italian Kitchen. I can help you make a reservation. What date were you thinking?"

**Caller:** "This Saturday evening, around 7."

**Agent:** "Let me check availability for Saturday at 7 PM. I have openings at 6:45 and 7:30. Which works better?"

**Caller:** "7:30 is fine."

**Agent:** "Great. How many people will be joining?"

**Caller:** "Four."

**Agent:** "Got it—table for 4 at 7:30 PM this Saturday. Can I get a name for the reservation?"

...and so on.

-----
## <a name="_fvhph8126c6r"></a>**Technical Requirements**
### <a name="_4ej0m3mfwbps"></a>**Core Components**

|**Component**|**Purpose**|**Suggested Tools**|
| :-: | :-: | :-: |
|**Plivo Voice API**|Handle inbound calls|Plivo SDK|
|**Audio Streaming**|Pipe real-time audio to/from the call|Plivo Audio Streaming (WebSocket)|
|**Speech-to-Text**|Convert caller speech to text|Deepgram, Google STT, or AssemblyAI|
|**LLM**|Process intent and generate responses|OpenAI GPT-4, Claude, or Groq|
|**Text-to-Speech**|Convert agent responses to audio|ElevenLabs, Deepgram TTS, or PlayHT|
|**Backend Server**|Orchestrate the entire flow|Python (Flask/FastAPI) or Node.js|
### <a name="_5nkeufadmipg"></a>**Architecture Flow**
****Inbound Call → Plivo → Audio Stream (WebSocket) → STT → LLM → TTS → Audio Stream → Caller

-----
## <a name="_emiapmb96w77"></a>**Timeline**
### <a name="_xruxdmbc3404"></a>**Day 1: Get Audio Flowing (Morning → Evening)**

|**Time Block**|**Task**|**Goal**|
| :-: | :-: | :-: |
|**Morning (3-4 hrs)**|Set up Plivo inbound number + audio streaming|Calls connect and you see raw audio data in your WebSocket server|
|**Afternoon (3-4 hrs)**|Integrate STT + TTS|Build a "parrot" app—caller speaks, hears their words repeated back|
|**Evening (1-2 hrs)**|Debug and stabilize|Clean call flow with no dropped connections or audio glitches|

**Day 1 Checkpoint:** You can call the number, speak, and hear your words echoed back via TTS.

-----
### <a name="_mak3ozkumcui"></a>**Day 2: Add the Brain (Morning → Demo)**

|**Time Block**|**Task**|**Goal**|
| :-: | :-: | :-: |
|**Morning (3-4 hrs)**|Integrate LLM with a reservation prompt|Agent responds contextually instead of parroting|
|**Afternoon (2-3 hrs)**|Implement conversation state tracking|Agent remembers what's been said, collects: date, time, party size, name|
|**Late Afternoon (2 hrs)**|Handle edge cases + polish|Add fallbacks for unclear input, optimize response latency|
|**End of Day**|Demo prep|Test 3-4 full reservation calls, fix any remaining issues|

**Day 2 Checkpoint:** Complete a full reservation conversation that feels reasonably natural.

-----
## <a name="_8nvmploo5u5x"></a>**Scope for This Sprint**
### <a name="_a056d285204v"></a>**In Scope (Must Have)**
- Inbound call answering with audio streaming
- Real-time STT → LLM → TTS pipeline
- Single use case: book a reservation (date, time, party size, name)
- Basic error handling ("Sorry, I didn't catch that")
### <a name="_99464ilgfygb"></a>**Out of Scope (Save for Later)**
- Barge-in / interruption handling
- Multi-language support
- Outbound calls or SMS follow-up
- Dashboard or analytics
- Production-grade error handling

Keep it simple. A working demo beats a polished failure.

-----
## <a name="_jjll97kafw47"></a>**Success Criteria**
Your agent is ready when it can:

1. **Answer a call** and greet the caller naturally
1. **Collect all required info** (date, time, party size, name) across multiple turns
1. **Confirm the reservation** back to the caller
1. **Handle one misheard input** gracefully (asks caller to repeat)
1. **Complete the flow** in under 2 minutes
-----
## <a name="_83xrgcgug5ip"></a>**Resources**
- [Plivo Voice API Docs](https://www.plivo.com/docs/voice/)
- [Plivo Audio Streaming Guide](https://www.plivo.com/docs/voice/use-cases/audio-streaming/)
- [Deepgram Streaming STT](https://developers.deepgram.com/docs/getting-started-with-live-streaming-audio)
- [OpenAI API](https://platform.openai.com/docs)
- [ElevenLabs TTS](https://elevenlabs.io/docs)
-----
## <a name="_xk030nmqsvjj"></a>**Deliverables**
1. **Working demo** — Call the number and complete a reservation
1. **GitHub repo** — Code with a basic README (doesn't need to be pretty)
1. **5-minute walkthrough** — Show the team: architecture, demo call, one thing you learned
-----
## <a name="_bt6kplp11phv"></a>**Tips for Moving Fast**
- **Hardcode the "availability."** Don't build a real database—just fake it.
