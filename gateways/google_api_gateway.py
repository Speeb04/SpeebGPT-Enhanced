from __future__ import annotations

from datetime import datetime

from google import genai
from google.genai import types

from gateways.singleton import Singleton


# NOTE: The API key is retrieved from the environment variable `GEMINI_API_KEY`.
class GoogleAPIGateway(metaclass=Singleton):
    """
    Each project should only implement at most one API Gateway.
    This is to avoid abuse and rate limiting.

    The Google Gemini API should be used for prompt-engineered focused responses.
    This is to reduce cost and rate limiting
    """
    _MODEL: str

    def __init__(self, model: str = "gemini-2.5-flash-lite"):
        self._MODEL = model
        self.client = genai.Client()

    @property
    def model(self) -> str:
        return self._MODEL

    @model.setter
    def model(self, model: str) -> None:
        self._MODEL = model

    def generate_response(self, instructions: str, content: str) -> str:
        """Main method to generate responses from Google's Gemini API"""
        response = self.client.models.generate_content(
            model=self._MODEL,
            config=types.GenerateContentConfig(
                system_instruction=instructions,
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            ),
            contents=content
        )

        return response.text

    # All method below are to generate responses in regards with prompt engineering to refine the output.

    flags = """
    song (--song):              anything to do with a song (even if not explicitly mentioned).
                                an input like "what song am I listening to currently?" would fall into this category.
                                However, messages only mentioning artists falls under the --artist flag.
                                So, an input like "can you tell me about Taylor Swift?" would not fall into this category.
                                If both a song and an artist is mentioned, default to song.
                                
                                Mentions to songs in general without a specific mention, like "can you tell me about this
                                artist's songs?" should default to the --artist flag.
    
    artist (--artist):          anything to do with a music artist (even if not explicitly mentioned).
                                an input like "who sang this song?" would fall into this category.

    weather (--weather):        anything to do with the current weather, like temperature, wind, sunrise/sunset, etc.

    web search (--web):         anything that has to do with a proper noun, or commonly becomes outdated,
                                for example, "who is the current president of the United States?"
                                something like a programming question or math question which relies on reasoning does not
                                need a web search, so this flag would be omitted.
                                Furthermore, if a prompt is vague, like "what is this image?" with none provided, this
                                should not receive the --web flag.
                                
                                If a user is searching for players relating to a sports team, like "who's the star player of
                                the Toronto Blue Jays?" should get the --web flag.
                            
    none of the above (--none): none of the above. Any message that mentions an image or a file (like, "what's in this image?")
                                should get this flag.
                            
    Note: all personal opinions lack flags. Even content such as "do you like Never Gonna Give You Up by Rick Astley"
    lacks the --music flag as that is a matter of personal opinion.
    """

    def get_flags(self, content: str) -> str:
        """Searches message content to get flags"""

        instructions = f"""
        Search the content below and choose one flag to output.
        The flags all start with two dashes, "--", and are listed below:
        
        {GoogleAPIGateway.flags}
        
        For example, given the prompt "who is the current president of the United States?",
        A response would be: "--web".
        """

        return self.generate_response(instructions, content)

    def search_engine_optimization(self, content: str) -> str:
        """Takes in message content and converts it into an SEO term for web
        searches (for messages that have the web search flag.)"""

        instructions = (f"Read the content of the user message and create an SEO term for one web search that can answer"
                        f"the user's query. Return only the SEO term and nothing else. "
                        f"Any references to time should also be included in the SEO term. Today is {datetime.strftime(datetime.now(), '%Y-%m-%d')}"
                        f"in Y/M/D format."
                        f"So, for example, if the query is"
                        f"'who won the super bowl this year?', the response would be 'super bowl {datetime.strftime(datetime.now(), '%Y')}'.")

        return self.generate_response(instructions, content)

    def attain_song_information(self, content: str) -> str:
        """Takes in message content about a song, and then determine the song's
        name and artist"""

        instructions = """
        Read the content of the user message and determine the song's name and artist.
        The output notation should be as follows: 
        song_name\n"artist1","artist2"
        
        For example, for the song Never Gonna Give You Up by Rick Astley, the output would be:
        Never Gonna Give You Up\n"Rick Astley"
        
        If the prompt starts with (The user is playing...) but they mention a different track
        later on, disregard the (The user is playing...) message at the top.
        """

        return self.generate_response(instructions, content)

    def attain_artist_information(self, content: str) -> str:
        """Takes in message content about a song, and then determine the song's
        name and artist"""

        instructions = """
        Read the content of the user message and determine the main artist mentioned.
        
        For example, if the user asks "who is Taylor Swift?", the output would be:
        "Taylor Swift"
        """

        return self.generate_response(instructions, content)

    def attain_location_information(self, content) -> str:
        """Takes in message content about a weather query, and then determines the location information to parse said
        weather query. If none found, raises IOError."""

        instructions = """
        Read the content of the user message and determine the location they want access to.
        The output notation should be as follows:
        city_name, two_letter_country_code
        
        For example, if the user query said "tell me about the weather in Toronto", the output would be:
        Toronto, CA
        
        If no city can be found, the output should be only "none".
        """

        output = self.generate_response(instructions, content)

        if output == "none":
            raise IOError("No location data found")

        return output
