CREATE TABLE `david_conversations` (
	`id` varchar(36) NOT NULL,
	`userId` int NOT NULL,
	`title` varchar(160) NOT NULL,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `david_conversations_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `david_memories` (
	`id` varchar(36) NOT NULL,
	`userId` int NOT NULL,
	`kind` enum('fact','preference','decision','learning','note') NOT NULL DEFAULT 'note',
	`content` text NOT NULL,
	`source` varchar(160) DEFAULT 'owner',
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `david_memories_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `david_messages` (
	`id` varchar(36) NOT NULL,
	`userId` int NOT NULL,
	`conversationId` varchar(36) NOT NULL,
	`role` enum('user','assistant') NOT NULL,
	`content` text NOT NULL,
	`model` varchar(96),
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `david_messages_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `david_projects` (
	`id` varchar(36) NOT NULL,
	`userId` int NOT NULL,
	`name` varchar(160) NOT NULL,
	`description` text,
	`status` enum('active','planning','complete','archived') NOT NULL DEFAULT 'active',
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `david_projects_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `david_runs` (
	`id` varchar(36) NOT NULL,
	`userId` int NOT NULL,
	`conversationId` varchar(36),
	`objective` text NOT NULL,
	`plan` text,
	`status` enum('queued','planning','waiting_approval','executing','complete','degraded','failed') NOT NULL DEFAULT 'queued',
	`provider` varchar(96),
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `david_runs_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `david_tasks` (
	`id` varchar(36) NOT NULL,
	`userId` int NOT NULL,
	`projectId` varchar(36),
	`title` varchar(240) NOT NULL,
	`description` text,
	`status` enum('todo','in_progress','blocked','done') NOT NULL DEFAULT 'todo',
	`priority` enum('low','normal','high') NOT NULL DEFAULT 'normal',
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `david_tasks_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `users` (
	`id` int AUTO_INCREMENT NOT NULL,
	`openId` varchar(64) NOT NULL,
	`name` text,
	`email` varchar(320),
	`loginMethod` varchar(64),
	`role` enum('user','admin') NOT NULL DEFAULT 'user',
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	`lastSignedIn` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `users_id` PRIMARY KEY(`id`),
	CONSTRAINT `users_openId_unique` UNIQUE(`openId`)
);
--> statement-breakpoint
CREATE INDEX `david_conversations_user_idx` ON `david_conversations` (`userId`);--> statement-breakpoint
CREATE INDEX `david_memories_user_idx` ON `david_memories` (`userId`);--> statement-breakpoint
CREATE INDEX `david_messages_conversation_idx` ON `david_messages` (`conversationId`);--> statement-breakpoint
CREATE INDEX `david_messages_user_idx` ON `david_messages` (`userId`);--> statement-breakpoint
CREATE INDEX `david_projects_user_idx` ON `david_projects` (`userId`);--> statement-breakpoint
CREATE INDEX `david_runs_user_idx` ON `david_runs` (`userId`);--> statement-breakpoint
CREATE INDEX `david_runs_conversation_idx` ON `david_runs` (`conversationId`);--> statement-breakpoint
CREATE INDEX `david_tasks_user_idx` ON `david_tasks` (`userId`);--> statement-breakpoint
CREATE INDEX `david_tasks_project_idx` ON `david_tasks` (`projectId`);