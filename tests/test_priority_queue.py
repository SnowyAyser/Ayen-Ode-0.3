from pathlib import Path
import unittest
import uuid
import time

from ayen_ode.service import AyenOdeService


class PriorityInvestigationQueueTests(unittest.TestCase):
    def setUp(self) -> None:
        self.db_root = Path.cwd() / "data" / "test-dbs"
        self.db_root.mkdir(parents=True, exist_ok=True)
        self.db_path = self.db_root / f"{uuid.uuid4().hex}.db"
        self.service = AyenOdeService(self.db_path)
        self.world = self.service.create_world("Linked World", "Setup for testing.")["world"]
        self.world_id = self.world["world_id"]

    def tearDown(self) -> None:
        for path in self.db_root.glob(f"{self.db_path.name}*"):
            path.unlink(missing_ok=True)

    def test_create_investigation_job_stores_priority(self) -> None:
        # 1. Default priority should be 1
        job1 = self.service.create_investigation_job("Entity A", "character", world=self.world_id)
        self.assertEqual(job1["priority"], 1)

        # 2. Specifying priority should persist
        job2 = self.service.create_investigation_job("Entity B", "location", world=self.world_id, priority=0)
        self.assertEqual(job2["priority"], 0)

        # 3. Retrieve and assert priority
        retrieved1 = self.service.get_investigation_job(job1["job_id"])
        self.assertEqual(retrieved1["priority"], 1)

        retrieved2 = self.service.get_investigation_job(job2["job_id"])
        self.assertEqual(retrieved2["priority"], 0)

    def test_get_investigation_queue_sorting(self) -> None:
        # Create standard-priority jobs
        job1 = self.service.create_investigation_job("Job A", "object", world=self.world_id, priority=1)
        time.sleep(0.01)
        job2 = self.service.create_investigation_job("Job B", "character", world=self.world_id, priority=1)
        time.sleep(0.01)

        # Create high-priority job (later chronologically)
        job3 = self.service.create_investigation_job("Job C", "location", world=self.world_id, priority=0)

        # Queue should be ordered by priority ASC, created_at ASC
        # So Job C (priority 0) must be first, followed by Job A then Job B
        queue = self.service.get_investigation_queue(world=self.world_id)
        jobs = queue["jobs"]
        
        self.assertEqual(len(jobs), 3)
        self.assertEqual(jobs[0]["job_id"], job3["job_id"])
        self.assertEqual(jobs[1]["job_id"], job1["job_id"])
        self.assertEqual(jobs[2]["job_id"], job2["job_id"])

    def test_prioritize_investigation_job(self) -> None:
        job = self.service.create_investigation_job("Test Item", "object", world=self.world_id, priority=1)
        self.assertEqual(job["priority"], 1)

        # Prioritize job
        self.service.prioritize_investigation_job(job["job_id"])

        retrieved = self.service.get_investigation_job(job["job_id"])
        self.assertEqual(retrieved["priority"], 0)

    def test_prioritize_investigation_job_by_name(self) -> None:
        # 1. Plural match test ("Toll Warden" vs "Toll Wardens")
        job = self.service.create_investigation_job("Toll Wardens", "character", world=self.world_id, priority=1)
        self.assertEqual(job["priority"], 1)

        # Prioritize singular name
        bumped = self.service.prioritize_investigation_job_by_name("Toll Warden", self.world_id)
        self.assertTrue(bumped)

        retrieved = self.service.get_investigation_job(job["job_id"])
        self.assertEqual(retrieved["priority"], 0)

        # 2. Singular match test ("Bridge" vs "Bridges")
        job2 = self.service.create_investigation_job("Bridge", "location", world=self.world_id, priority=1)
        
        # Prioritize plural name
        bumped2 = self.service.prioritize_investigation_job_by_name("Bridges", self.world_id)
        self.assertTrue(bumped2)

        retrieved2 = self.service.get_investigation_job(job2["job_id"])
        self.assertEqual(retrieved2["priority"], 0)


if __name__ == "__main__":
    unittest.main()
