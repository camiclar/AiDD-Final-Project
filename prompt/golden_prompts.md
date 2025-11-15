# Golden Prompts

## Building the Browse Resources Page
- Tool: Cursor
- Prompt: Perfect, now let's start working on core functionality. I think the best place to start would be the Resource Listings. This would be the "Browse Resources" screen from the prototype. Please implement the following requirements for the resource listings:
  - CRUD operations for resources: title, description, images, category, location, availability rules, owner (user/team), capacity, and optional equipment lists.
  - Listing lifecycle: draft, published, archived.
  - For the visual side of things, use the AiDD-Final-Wireframes-Combined.pdf file and Prototype Code for reference.
- Outcome: Cursor implemented registration and login, the Browse Resources page including searching and filtering, and creating new resources. It included way more features than I anticipated, so I had to carefully review everything to make sure it all functions properly. Additionally, it did not style the visuals like the wireframe, instead just using default Bootstrap. I am keeping all of its work for now, but may change the visuals and need to address any issues that come up.


## Adding an AI Admin Assistant
- Tool: Cursor & Google AI Studio
- Prompt: A new folder has been added to your context at docs\context\shared\GEMINI_DRIVEN_WEBSITE. This is a demo of a website in which a user can write in natural language and the Google Gemini API can translate the user's request into SQL which will then pull database results, producing a human-readable output. As an example, a user could type "What were the top 3 selling products over the last year", and the site would analyze database data and produce an answer. I want to implement something similar for the Campus Resource Hub. What I'm imagining is a little chatbot on the admin dashboard that would allow admins to ask questions about usage of resources. So things like "What time of day do most resources get booked for?" I'm not totally sure about how the API key piece of this would work. I got a free API key for Google Gemini that could probably be used for this. The thing is, I want to avoid uploading my API key to the GitHub repo, but I also want to deploy this webiste on the web. Is there a way to store the API key in this project so the site can be published on the web with the chatbot being functional, while avoiding uploading my API key to GitHub?
- Outcome: Cursor used the Gemini Demo site as a reference to create a new natural language analytics assistant on the admin panel. It took multiple iterations and some experimenting with API keys to get it to work, but I kept most of the original functionality that Cursor created.
