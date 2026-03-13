from __future__ import annotations

import os

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class TodayInternationalNewsCrew:
    """CrewAI definition for short-form international news video planning."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    model_name = os.getenv("OPENAI_MODEL_NAME") or "gpt-4o-mini"

    @agent
    def news_editor(self) -> Agent:
        return Agent(
            config=self.agents_config["news_editor"],
            llm=self.model_name,
            verbose=True,
        )

    @agent
    def script_producer(self) -> Agent:
        return Agent(
            config=self.agents_config["script_producer"],
            llm=self.model_name,
            verbose=True,
        )

    @agent
    def visual_director(self) -> Agent:
        return Agent(
            config=self.agents_config["visual_director"],
            llm=self.model_name,
            verbose=True,
        )

    @agent
    def quality_editor(self) -> Agent:
        return Agent(
            config=self.agents_config["quality_editor"],
            llm=self.model_name,
            verbose=True,
        )

    @task
    def select_news(self) -> Task:
        return Task(
            config=self.tasks_config["select_news"],
            agent=self.news_editor(),
        )

    @task
    def create_video_package(self) -> Task:
        return Task(
            config=self.tasks_config["create_video_package"],
            agent=self.script_producer(),
            context=[self.select_news()],
        )

    @task
    def visual_polish_package(self) -> Task:
        return Task(
            config=self.tasks_config["visual_polish_package"],
            agent=self.visual_director(),
            context=[self.create_video_package()],
        )

    @task
    def review_video_package(self) -> Task:
        return Task(
            config=self.tasks_config["review_video_package"],
            agent=self.quality_editor(),
            context=[self.visual_polish_package()],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
