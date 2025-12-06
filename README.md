# SpeebGPT Enhanced

## Table of Contents:
1. [Overview and FAQ - about SpeebGPT](#overview)
2. [Commands - how to use](#commands)
3. [Integrations - APIs, third party sites](#integrations)
4. [Privacy Notice - how your data is collected and used](#privacy-notice)

## Overview

**SpeebGPT** is an AI powered bot to help assist you in Discord. **It currently supports the following features:**
- Web search (via Brave search)
- Weather (via Openweathermap)
- Music information (via Genius)
- Image understanding
- File understanding

**If you're curious about how each of these services are used,** [click here.](#integrations)  
**To understand how your data is being collected and used,** [click here.](#privacy-notice)

### Frequently Asked Questions (FAQ):
> *Q: Does SpeebGPT support image generation?*  

**No.** The reason is due to the ethical ambiguity of AI-generated images - 
specifically, qualms with the lack of originality with AI-derivative works and 
plagiarism from real human artists and their work.

> *Q: How are conversations stored?*  

**They're not - at least not permanently.** Discussions and interactions should 
be fleeting - savoured in the moment, and then lost to the sands of time. For 
this reason, all conversations are *volatile* and the history is deleted for 
each restart of the bot.

**Furthermore,** the conversation history is limited to 10 messages at most by 
default (which includes messages from both the user and the assistant). **With 
each message added** to the conversation, the system checks for conversation
length and ensures that the server is not having to send too many updates to
ensure optimal performance.

> *Q: Does SpeebGPT use ChatGPT or Gemini?*

**In short - yes.**  
Okay, I'll elaborate. SpeebGPT's backend uses *both* services for a plethora of 
reasons - which I will delve into **after** describing how each service is 
being used.

**Message pipeline overview:**

&nbsp;&nbsp;&nbsp;&nbsp;**message sent -> add flags -> integration** *(optional)* **-> generate response -> send response**  

In short, **Gemini 2.5 Flash-Lite** handles the flags and integration section for the flags and the integrations.  
This is due to Gemini's _lower cost_ as it handles the lower reasoning but higher quantity queries.  

**GPT 5 Nano,** however, handles the real response generation along with the reasoning to process that response.
This is mainly due to the OpenAI library being more open to varied chat history structure to better suit SpeebGPT's use case.

> *Q: Did AI have any role in writing this document?*  

**No,** but in hindsight, maybe it should've.

## Commands

**Currently,** no slash commands are implemented, but *check back later.*

### `@on_message`
If the message starts with a greeting like **"hi", "hey",** or **"yo"** followed by 
one of SpeebGPT's aliases (like **Speeb** or **Speebot**), it will **initiate a conversation.**

_Mentioning SpeebGPT_ will also **initiate a conversation.**

**To continue a conversation,** reply to the message that SpeebGPT sent and it will follow up with you.

## Integrations

* ### [Web Searches (via `api.search.brave.com`)](https://brave.com/search/api/)
    SpeebGPT uses the **Brave Search API** to help complete prompts that require 
    web searches.  
    _Typically_, this is anything with a **proper noun** or time-related query.
* ### [Weather Information (via `api.openweathermap.org`)](https://openweathermap.org/)
    SpeebGPT uses the **OpenWeatherMap API** to fetch current weather information 
    about a given location.  
    Only _current weather information_ is retrieved - forecasting information is omitted.
* ### [Music Information (via `api.genius.com`)](https://docs.genius.com/)
    SpeebGPT uses the **Genius API** to parse information about songs and artists.
    > *Q: Can SpeebGPT access song lyric information?*

    **No -** while the idea is interesting and fun, Genius's **lyric information** is their 
    intellectual property as it involves work to write and attain lyric information for songs.
* ### [Google Gemini](https://ai.google.dev/gemini-api/docs)
    As previously stated, **SpeebGPT** uses **Google's Gemini API** to attain flags and other 
    language-related queries that use limited reasoning.
* ### [OpenAI](https://openai.com/api/)
    Also stated previously, **SpeebGPT** uses **OpenAI's chat completion API** to process user 
    input and give an output with structured reasoning.
    Furthermore, **image understanding and file parsing** is also done though the OpenAI platform.

## Privacy Notice
Please read the following to understand how your personal data is being collected and used,
as well as how AI outputs may present as dangerous or harmful.
### 1. Warnings for generative AI chat outputs
*  **SpeebGPT can make mistakes.** Modern generative AI models use statistical models to create outputs, 
commonly using [Markov chains.](https://en.wikipedia.org/wiki/Markov_chain) This means that these models
are programmed to give the most **statistically likely** outcome, rather than the one that is most factually 
accurate. **SpeebGPT may take factually inaccurate information or subjective options and present them as
objective information.** Check all important information through multiple reputable sources.  


* **SpeebGPT may send dangerous or offensive content.** While we work hard to protect end users from harmful
content, a consequence of using external models for responses means that we cannot control their outputs. **At most, 
we can apply a moderation filter** for specific keywords that may cause offence.

### 2. How SpeebGPT collects your information
* **SpeebGPT does not** store any personal information about you for commercial purposes. Only text information is stored,
and it is anonymized so that no user data can be traced back beyond your Discord information. As all conversations are volatile, 
this message data is erased on restart of the bot.  


* **SpeebGPT can see** your message data and your public activity presence (i.e, your Spotify activity on your profile) when you 
ask about music information. **SpeebGPT cannot see** any non-public information, such as emails and phone numbers, or previous
account information.


* **SpeebGPT will only parse messages** that include a wakeup call (i.e. *"Hey Speeb..."*). **The content of ALL messages are checked**
 for the wakeup phrase, but **no data is retained or used unless a call to the bot is explicity made.**


* **By using SpeebGPT**, you consent to allowing the bot and all utilized services to use your message information (including 
activity presence data) to be collected and used by third-party services to help provide chatting services.


### 3. How other services may collect your information
* **NOTE:** your personal data **may be collected** by the integrations used by SpeebGPT to generate responses.  
**In particular, Gemini collects content to "improve our products." [Learn more here.](https://ai.google.dev/gemini-api/terms)**


* **Furthermore**, SpeebGPT has no control over how **OpenAI, OpenWeatherMap, Genius, or other integrated services** collect your 
user data or how its utilized.


* **Your data is anonymized.** When you send information through these services, no personal information is sent beyond the contents
of the message. **For this reason, we highly recommend you NOT include personal information in message content.**


* **No metadata is included.** All calls to APIs lack metadata and cannot be used to trace back to you. The only difference is the
content of the message or activity presences.
