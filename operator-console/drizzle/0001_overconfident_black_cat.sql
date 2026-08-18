CREATE TABLE `david_run_events` (
	`id` varchar(36) NOT NULL,
	`userId` int NOT NULL,
	`runId` varchar(36) NOT NULL,
	`type` enum('goal_received','plan_created','model_selected','response_streaming','verification_started','verification_passed','run_degraded','run_failed') NOT NULL,
	`state` enum('planning','thinking','executing','verifying','complete','degraded','failed') NOT NULL,
	`actor` varchar(96) NOT NULL DEFAULT 'David AI',
	`summary` varchar(500) NOT NULL,
	`provider` varchar(96),
	`metadata` text,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `david_run_events_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE INDEX `david_run_events_run_idx` ON `david_run_events` (`runId`);--> statement-breakpoint
CREATE INDEX `david_run_events_user_idx` ON `david_run_events` (`userId`);