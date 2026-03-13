import os

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class TodayInternationalNewsCrew:
    """CrewAI definition for generating a daily international news report."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

    @agent
    def news_editor(self) -> Agent:
        return Agent(
            config=self.agents_config["news_editor"],
            llm=self.model_name,
            verbose=True,
        )

    @agent
    def quality_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["quality_reviewer"],
            llm=self.model_name,
            verbose=True,
        )

    @task
    def select_and_summarize_news(self) -> Task:
        return Task(
            config=self.tasks_config["select_and_summarize_news"],
        )

    @task
    def review_report(self) -> Task:
        return Task(
            config=self.tasks_config["review_report"],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
