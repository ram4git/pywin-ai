Use the same style and design language as that of root vision-studio project for any UI/UX decision

Build a webapp that shows a text area to enter a prompt and when submitted, use llm to create sequence of PyWinAuto instructions to acchieve that task and show the button to run. When run, execute the automation on the current windows computer. If it fails, give an option to prompt again and refine the PyWinAuto script and give options to run again. Also give an option to save the script with a name. Show a tab to see all saved PyWinAuto scripts and if selected show them the same prompt, and instructions conected to the prompt and give a way to run the PyWinAuto script.

This application has to run on Windows computer so come with strategies on how to package it (docker for windows?) or exe file.\
\
Have an .env file to specify the llm endpoint and API key just like we have in the root of the project and use it for making llm requests.

This is primarily for Windows and most tasks would do something like opening up a windows application and click and do operations on top of it. It would involve opening mulitple windows applications and copying date to and from from the application. A good example would be Open MSSQLStudio and run a query, copy the query response table and use excel to produce a graphic and copy the graph to an outlook email and compose it by summerizing the graph and send email.
