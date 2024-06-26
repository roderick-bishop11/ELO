# E.L.O. proof of concept - aka "assistant"

## Objective

ELO = Enhanced Logical Operative
To create an environment control plane entity powered by AI.

## Scope

This project is meant to be POC work. "Garage time", if you will.

No R.A.G. for this project, however MoE may be explored.

## Inspiration

Tony Stark, J.A.R.V.I.S. and Robert Elo Bishop(my grandfather). ELO is meant to be more than an assistant. If you think of Operating Systems working on computers, think of ELO as an *operative*. Another way to define the concept is a Semi-Autonomous AI powered operative working on your behalf. Outfit with integrations, standard library of defined functions, local access, and intuitive interfacing.

## Desired state/Feature Set

"Assistant (this folder) is meant to be the POC for ELO. In this I'd like to accomplish or deliver on this basic feature set:

- Chat GPT integration or Local LLM generation; The option to choose/switch models.
- Internet Search (whitelisted sources)
- Wake and shut down word/phrases/intents
- Modes for verbose logging/print out

## Possible tech stack/modules/tools to use

- [Python](https://www.python.org/)- language
- [Poetry](https://python-poetry.org/)- build system
  - Poetry w/Python makes me appreciate Gradle/Maven for JVM projects. The full suite of tasks/Lifecycle phase commands are cool accessible directly through the same CLI is wonderful.
- [pyttsx4](https://pypi.org/project/pyttsx4/) or [Eleven labs](https://elevenlabs.io/)- Text to speech
- [OpenAI API](https://platform.openai.com/docs/overview)- interact with models
- [Exa](https://github.com/exa-labs/exa-py)- Search for AI
- [Pre-Commmit](https://pre-commit.com/)- for pre-commit tasks

## To do

- fix logger
- visualize the sound coming back from elevel labs.

## Changelog

- 3.8.24: Got instruction on project organization/implementation. Separate part into epics/bodies of work. Could use JIRA or some other tool to organize and stay on track. Simplify README & develop a more clear project. 
