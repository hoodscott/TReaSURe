BEGIN TRANSACTION;
CREATE TABLE "treasure_webresource" (
    "id" integer NOT NULL PRIMARY KEY,
    "resource_id" integer NOT NULL UNIQUE REFERENCES "treasure_resource" ("id"),
    "url" varchar(200) NOT NULL
);
INSERT INTO `treasure_webresource` VALUES (1,3,'http://www.python.org/');
INSERT INTO `treasure_webresource` VALUES (2,4,'http://java.com/');
INSERT INTO `treasure_webresource` VALUES (3,12,'http://www.youtube.com/');
CREATE TABLE "treasure_teacherwantstotalkresource" (
    "id" integer NOT NULL PRIMARY KEY,
    "teacher_id" integer NOT NULL REFERENCES "treasure_teacher" ("id"),
    "resource_id" integer NOT NULL REFERENCES "treasure_resource" ("id"),
    "comment" text NOT NULL
);
INSERT INTO `treasure_teacherwantstotalkresource` VALUES (1,4,1,'I have tried it and it worked');
CREATE TABLE "treasure_teacherusesresource" (
    "id" integer NOT NULL PRIMARY KEY,
    "teacher_id" integer NOT NULL REFERENCES "treasure_teacher" ("id"),
    "resource_id" integer NOT NULL REFERENCES "treasure_resource" ("id"),
    "download_id" integer NOT NULL REFERENCES "treasure_teacherdownloadsresource" ("id"),
    "latitude" real NOT NULL,
    "longitude" real NOT NULL,
    "rated" bool NOT NULL
);
CREATE TABLE "treasure_teacherratesresource" (
    "id" integer NOT NULL PRIMARY KEY,
    "teacher_id" integer NOT NULL REFERENCES "treasure_teacher" ("id"),
    "resource_id" integer NOT NULL REFERENCES "treasure_resource" ("id"),
    "measure1" varchar(128) NOT NULL,
    "measure2" varchar(128) NOT NULL,
    "measure3" varchar(128) NOT NULL,
    "comment" text NOT NULL
);
INSERT INTO `treasure_teacherratesresource` VALUES (1,4,1,'5','5','5','Perfect');
INSERT INTO `treasure_teacherratesresource` VALUES (2,3,2,'4','4','4','Too much jargon');
INSERT INTO `treasure_teacherratesresource` VALUES (3,1,3,'3','3','3','Bad timing');
CREATE TABLE "treasure_teacherdownloadsresource" (
	`id`	integer NOT NULL,
	`teacher_id`	integer NOT NULL,
	`resource_id`	integer NOT NULL,
	`used`	INTEGER NOT NULL,
	`datetime`	INTEGER,
	`latitude`	REAL,
	`longitude`	REAL,
	`rated`	INTEGER,
	PRIMARY KEY(id)
);
INSERT INTO `treasure_teacherdownloadsresource` VALUES (1,1,2,0,'2015-12-30 05:18:56.664262',1.0,1.0,0);
INSERT INTO `treasure_teacherdownloadsresource` VALUES (2,5,2,0,'2015-12-30 06:33:43.273210',1.6,1.25,0);
INSERT INTO `treasure_teacherdownloadsresource` VALUES (3,4,2,1,'2015-12-30 06:33:43.273210',2.0,2.0,0);
INSERT INTO `treasure_teacherdownloadsresource` VALUES (4,3,2,1,'2015-12-30 06:33:43.273210',3.0,3.0,0);
CREATE TABLE "treasure_teacher_hubs" (
    "id" integer NOT NULL PRIMARY KEY,
    "teacher_id" integer NOT NULL,
    "hub_id" integer NOT NULL REFERENCES "treasure_hub" ("id"),
    UNIQUE ("teacher_id", "hub_id")
);
INSERT INTO `treasure_teacher_hubs` VALUES (1,1,1);
INSERT INTO `treasure_teacher_hubs` VALUES (2,1,2);
INSERT INTO `treasure_teacher_hubs` VALUES (3,2,2);
INSERT INTO `treasure_teacher_hubs` VALUES (4,4,1);
INSERT INTO `treasure_teacher_hubs` VALUES (5,7,1);
CREATE TABLE "treasure_teacher" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id"),
    "firstname" varchar(128) NOT NULL,
    "surname" varchar(128) NOT NULL,
    "school_id" integer REFERENCES "treasure_school" ("id")
);
INSERT INTO `treasure_teacher` VALUES (1,1,'Billy','Connolly',1);
INSERT INTO `treasure_teacher` VALUES (2,2,'Scott','Hood',3);
INSERT INTO `treasure_teacher` VALUES (3,3,'Hood','Scott',3);
INSERT INTO `treasure_teacher` VALUES (4,4,'Sir Iain-Gerard','MacCionaodha',5);
INSERT INTO `treasure_teacher` VALUES (5,5,'Quintin','Cutts',1);
INSERT INTO `treasure_teacher` VALUES (6,6,'Nigel','Clarke',4);
INSERT INTO `treasure_teacher` VALUES (7,7,'Brad','Pitt',4);
CREATE TABLE "treasure_tag" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(128) NOT NULL,
    "type" varchar(1) NOT NULL
);
INSERT INTO `treasure_tag` VALUES (1,'National 5','0');
INSERT INTO `treasure_tag` VALUES (2,'National 4','0');
INSERT INTO `treasure_tag` VALUES (3,'Higher','0');
INSERT INTO `treasure_tag` VALUES (4,'Advanced Higher','0');
INSERT INTO `treasure_tag` VALUES (5,'Information Systems','1');
INSERT INTO `treasure_tag` VALUES (6,'Programming','1');
INSERT INTO `treasure_tag` VALUES (7,'Java','2');
INSERT INTO `treasure_tag` VALUES (8,'Python','2');
CREATE TABLE "treasure_school" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(128) NOT NULL,
    "town" varchar(128) NOT NULL,
    "address" text NOT NULL,
    "latitude" real NOT NULL,
    "longitude" real NOT NULL
);
INSERT INTO `treasure_school` VALUES (1,'Clydebank High School','Clydebank','56 Attlee Avenue
Linnvale',1.0,1.0);
INSERT INTO `treasure_school` VALUES (2,'St Peter the Apostle','Clydebank','34 Streetname',1.0,2.0);
INSERT INTO `treasure_school` VALUES (3,'Edinburgh High School','Edinburgh','address',123.0,123.0);
INSERT INTO `treasure_school` VALUES (4,'HighSchool of Glasgow','Glasgow','AnnieslandX',90.0,-90.0);
INSERT INTO `treasure_school` VALUES (5,'Avery LongSchool Name','Atlantis','Atlantis',0.0,0.0);
CREATE TABLE "treasure_resource_tags" (
    "id" integer NOT NULL PRIMARY KEY,
    "resource_id" integer NOT NULL,
    "tag_id" integer NOT NULL REFERENCES "treasure_tag" ("id"),
    UNIQUE ("resource_id", "tag_id")
);
INSERT INTO `treasure_resource_tags` VALUES (3,2,2);
INSERT INTO `treasure_resource_tags` VALUES (22,2,8);
INSERT INTO `treasure_resource_tags` VALUES (23,2,4);
INSERT INTO `treasure_resource_tags` VALUES (24,2,6);
INSERT INTO `treasure_resource_tags` VALUES (28,11,1);
INSERT INTO `treasure_resource_tags` VALUES (29,10,2);
INSERT INTO `treasure_resource_tags` VALUES (30,10,6);
INSERT INTO `treasure_resource_tags` VALUES (31,10,7);
INSERT INTO `treasure_resource_tags` VALUES (32,9,4);
INSERT INTO `treasure_resource_tags` VALUES (33,9,5);
INSERT INTO `treasure_resource_tags` VALUES (34,8,1);
INSERT INTO `treasure_resource_tags` VALUES (35,7,2);
INSERT INTO `treasure_resource_tags` VALUES (36,7,6);
INSERT INTO `treasure_resource_tags` VALUES (37,6,2);
INSERT INTO `treasure_resource_tags` VALUES (38,6,6);
INSERT INTO `treasure_resource_tags` VALUES (39,5,8);
INSERT INTO `treasure_resource_tags` VALUES (40,5,4);
INSERT INTO `treasure_resource_tags` VALUES (41,5,6);
INSERT INTO `treasure_resource_tags` VALUES (42,4,1);
INSERT INTO `treasure_resource_tags` VALUES (43,4,2);
INSERT INTO `treasure_resource_tags` VALUES (44,4,3);
INSERT INTO `treasure_resource_tags` VALUES (45,4,4);
INSERT INTO `treasure_resource_tags` VALUES (46,4,6);
INSERT INTO `treasure_resource_tags` VALUES (47,4,7);
INSERT INTO `treasure_resource_tags` VALUES (48,3,1);
INSERT INTO `treasure_resource_tags` VALUES (49,3,2);
INSERT INTO `treasure_resource_tags` VALUES (50,3,3);
INSERT INTO `treasure_resource_tags` VALUES (51,3,4);
INSERT INTO `treasure_resource_tags` VALUES (52,3,6);
INSERT INTO `treasure_resource_tags` VALUES (53,3,8);
INSERT INTO `treasure_resource_tags` VALUES (54,1,1);
INSERT INTO `treasure_resource_tags` VALUES (55,1,4);
INSERT INTO `treasure_resource_tags` VALUES (56,12,4);
INSERT INTO `treasure_resource_tags` VALUES (57,12,3);
INSERT INTO `treasure_resource_tags` VALUES (58,12,5);
INSERT INTO `treasure_resource_tags` VALUES (59,12,7);
INSERT INTO `treasure_resource_tags` VALUES (60,12,2);
INSERT INTO `treasure_resource_tags` VALUES (61,12,1);
INSERT INTO `treasure_resource_tags` VALUES (62,12,6);
INSERT INTO `treasure_resource_tags` VALUES (63,12,8);
CREATE TABLE "treasure_resource_packs" (
    "id" integer NOT NULL PRIMARY KEY,
    "resource_id" integer NOT NULL,
    "pack_id" integer NOT NULL REFERENCES "treasure_pack" ("id"),
    UNIQUE ("resource_id", "pack_id")
);
INSERT INTO `treasure_resource_packs` VALUES (1,2,1);
INSERT INTO `treasure_resource_packs` VALUES (4,2,4);
INSERT INTO `treasure_resource_packs` VALUES (5,2,5);
INSERT INTO `treasure_resource_packs` VALUES (15,8,1);
INSERT INTO `treasure_resource_packs` VALUES (16,8,3);
INSERT INTO `treasure_resource_packs` VALUES (17,7,3);
INSERT INTO `treasure_resource_packs` VALUES (18,7,4);
INSERT INTO `treasure_resource_packs` VALUES (19,7,7);
INSERT INTO `treasure_resource_packs` VALUES (20,6,8);
INSERT INTO `treasure_resource_packs` VALUES (21,5,1);
INSERT INTO `treasure_resource_packs` VALUES (22,3,6);
INSERT INTO `treasure_resource_packs` VALUES (23,3,7);
INSERT INTO `treasure_resource_packs` VALUES (24,1,3);
CREATE TABLE "treasure_resource" (
	`id`	integer NOT NULL,
	`name`	varchar(128) NOT NULL,
	`tree`	text,
	`author_id`	integer NOT NULL,
	`description`	text NOT NULL,
	`summary`	varchar(128),
	`evolution_type`	varchar(128),
	`hidden`	INTEGER,
	`restricted`	INTEGER,
	`resource_type`	varchar(128),
	PRIMARY KEY(id),
	FOREIGN KEY(`author_id`) REFERENCES "treasure_teacher" ( "id" )
);
INSERT INTO `treasure_resource` VALUES (1,'Databases 101','1',4,'Introduction to DB',NULL,NULL,NULL,NULL,NULL);
INSERT INTO `treasure_resource` VALUES (2,'Project Euler','2',1,'Solution to the first project euler problem.',NULL,NULL,NULL,NULL,NULL);
INSERT INTO `treasure_resource` VALUES (3,'Python Website','3',1,'Official python website',NULL,NULL,NULL,NULL,NULL);
INSERT INTO `treasure_resource` VALUES (4,'Java Website','4',1,'Official java website',NULL,NULL,NULL,NULL,NULL);
INSERT INTO `treasure_resource` VALUES (5,'Project EUler Improved','2,5',1,'imporvement on the original',NULL,NULL,NULL,NULL,NULL);
INSERT INTO `treasure_resource` VALUES (6,'CT 101','6',2,'Thinking Like a machine',NULL,NULL,NULL,NULL,NULL);
INSERT INTO `treasure_resource` VALUES (7,'CT 101 Homework','7',3,'Homework for CT 101',NULL,NULL,NULL,NULL,NULL);
INSERT INTO `treasure_resource` VALUES (8,'HTML 101','8',1,'Introduction to HTML',NULL,NULL,NULL,NULL,NULL);
INSERT INTO `treasure_resource` VALUES (9,'Cyber Security','9',2,'Cyber Security Awareness',NULL,NULL,NULL,NULL,NULL);
INSERT INTO `treasure_resource` VALUES (10,'Java','10',4,'Java Basics',NULL,NULL,NULL,NULL,NULL);
INSERT INTO `treasure_resource` VALUES (11,'Python','11',2,'Introduction to Python',NULL,NULL,NULL,NULL,NULL);
INSERT INTO `treasure_resource` VALUES (12,'Computing Videos','12',1,'Collection of videos.',NULL,NULL,NULL,NULL,NULL);
CREATE TABLE "treasure_poi" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(100) NOT NULL,
    "position" varchar(42) NOT NULL
);
CREATE TABLE "treasure_pack_tags" (
    "id" integer NOT NULL PRIMARY KEY,
    "pack_id" integer NOT NULL,
    "tag_id" integer NOT NULL REFERENCES "treasure_tag" ("id"),
    UNIQUE ("pack_id", "tag_id")
);
INSERT INTO `treasure_pack_tags` VALUES (1,1,4);
INSERT INTO `treasure_pack_tags` VALUES (2,1,2);
INSERT INTO `treasure_pack_tags` VALUES (3,1,3);
INSERT INTO `treasure_pack_tags` VALUES (4,2,2);
INSERT INTO `treasure_pack_tags` VALUES (5,2,3);
INSERT INTO `treasure_pack_tags` VALUES (6,2,4);
INSERT INTO `treasure_pack_tags` VALUES (7,2,6);
INSERT INTO `treasure_pack_tags` VALUES (8,3,5);
INSERT INTO `treasure_pack_tags` VALUES (9,3,2);
INSERT INTO `treasure_pack_tags` VALUES (10,3,3);
INSERT INTO `treasure_pack_tags` VALUES (11,3,7);
INSERT INTO `treasure_pack_tags` VALUES (12,3,8);
CREATE TABLE "treasure_pack" (
	`id`	integer NOT NULL,
	`name`	varchar(128) NOT NULL,
	`author_id`	integer NOT NULL,
	`description`	TEXT NOT NULL,
	`image`	varchar(128) NOT NULL,
	`explore`	integer NOT NULL,
	`summary`	varchar(128),
	`hidden`	INTEGER,
	`restricted`	INTEGER,
	PRIMARY KEY(id)
);
INSERT INTO `treasure_pack` VALUES (1,'Project Euler',1,'PAck of euler solutions','http://vignette4.wikia.nocookie.net/mrmen/images/5/52/Small.gif/revision/latest?cb=20100731114437',1,NULL,NULL,NULL);
INSERT INTO `treasure_pack` VALUES (2,'Variables',2,'Variables in a nutshell','https://openresty.org/download/image/value-container.jpg',1,NULL,NULL,NULL);
INSERT INTO `treasure_pack` VALUES (3,'Computational Thinking',6,'SQA: All you need to know about computers','http://compthink.cs.depaul.edu/images/twoHead2.jpg',1,NULL,NULL,NULL);
INSERT INTO `treasure_pack` VALUES (4,'Programming',5,'SQA: "Computing is Programming"','http://www.unixmen.com/wp-content/uploads/2015/10/Programming-and-its-ways.png',1,NULL,NULL,NULL);
INSERT INTO `treasure_pack` VALUES (5,'Cyber Security',5,'Cyber Security Lesson Plan','http://uwf.edu/media/cybersecurity/Cyber-Security-(2).jpg',1,NULL,NULL,NULL);
INSERT INTO `treasure_pack` VALUES (6,'Web design',6,'Good Collection of Web Design Materials','http://tweetiepiemedia.com/wp-content/uploads/2014/04/webdesign.jpg',1,NULL,NULL,NULL);
INSERT INTO `treasure_pack` VALUES (7,'Iain''s Plan',4,'Personal Plan of Iain-Gerard','http://images.clipartpanda.com/stack-of-paper-clipart-stack-paper.gif',0,NULL,NULL,NULL);
INSERT INTO `treasure_pack` VALUES (8,'HSoG 2015',6,'Teaching Plan of HSoG for Year 2015','http://teachmeet.pbworks.com/f/1369951445/HSOG_TM_LOGO.png',0,NULL,NULL,NULL);
CREATE TABLE "treasure_hub" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(128) NOT NULL,
    "address" text NOT NULL,
    "latitude" real NOT NULL,
    "longitude" real NOT NULL
);
INSERT INTO `treasure_hub` VALUES (1,'Southern Hub','address',123.0,123.0);
INSERT INTO `treasure_hub` VALUES (2,'Northern Hub','address',25.0,3.0);
CREATE TABLE "treasure_filesresource" (
    "id" integer NOT NULL PRIMARY KEY,
    "resource_id" integer NOT NULL UNIQUE REFERENCES "treasure_resource" ("id"),
    "path" varchar(100) NOT NULL
);
INSERT INTO `treasure_filesresource` VALUES (2,2,'resources/2015/12/13/e1_2.py');
CREATE TABLE "social_auth_usersocialauth" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "provider" varchar(32) NOT NULL,
    "uid" varchar(255) NOT NULL,
    "extra_data" text NOT NULL,
    UNIQUE ("provider", "uid")
);
CREATE TABLE "social_auth_nonce" (
    "id" integer NOT NULL PRIMARY KEY,
    "server_url" varchar(255) NOT NULL,
    "timestamp" integer NOT NULL,
    "salt" varchar(65) NOT NULL,
    UNIQUE ("server_url", "timestamp", "salt")
);
CREATE TABLE "social_auth_code" (
    "id" integer NOT NULL PRIMARY KEY,
    "email" varchar(254) NOT NULL,
    "code" varchar(32) NOT NULL,
    "verified" bool NOT NULL,
    UNIQUE ("email", "code")
);
CREATE TABLE "social_auth_association" (
    "id" integer NOT NULL PRIMARY KEY,
    "server_url" varchar(255) NOT NULL,
    "handle" varchar(255) NOT NULL,
    "secret" varchar(255) NOT NULL,
    "issued" integer NOT NULL,
    "lifetime" integer NOT NULL,
    "assoc_type" varchar(64) NOT NULL
);
CREATE TABLE "django_site" (
    "id" integer NOT NULL PRIMARY KEY,
    "domain" varchar(100) NOT NULL,
    "name" varchar(50) NOT NULL
);
INSERT INTO `django_site` VALUES (1,'example.com','example.com');
CREATE TABLE "django_session" (
    "session_key" varchar(40) NOT NULL PRIMARY KEY,
    "session_data" text NOT NULL,
    "expire_date" datetime NOT NULL
);
INSERT INTO `django_session` VALUES ('x5mdz5ynn1lepcmwplz3k7nnzkzqx4xz','MTViYjFkNmNjOGRlZjEyNzM0NzkwYTcwNzJhMzZjNDcwNmVkMmMyYzp7Il9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6MX0=','2015-12-27 05:30:26.552000');
INSERT INTO `django_session` VALUES ('uo877uoqzndshsr3s8gyqn8lhb9orz80','MTViYjFkNmNjOGRlZjEyNzM0NzkwYTcwNzJhMzZjNDcwNmVkMmMyYzp7Il9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6MX0=','2015-12-28 09:04:09.779208');
INSERT INTO `django_session` VALUES ('qu5ue6zmh5cjwr8tkuolfmzyx3zaxfzi','YzBhOGU0YTg0ZWY3NzhiOTM5NTZhMWNjNjU5MTVjODUwMzAwMzEzZTqAAn1xAShVEl9hdXRoX3VzZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHEDVQ1fYXV0aF91c2VyX2lkcQRLAXUu','2015-12-28 14:35:23.134180');
INSERT INTO `django_session` VALUES ('bw5kx27nj0c59yqk29gvkei4rennpfny','YmNlZjY5ODk1NGU4MjJlMWNmZjQwNmM0MDJjZmMxYjEyYWZiNTRkZDp7Il9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9pZCI6Nn0=','2015-12-30 11:54:08.874132');
INSERT INTO `django_session` VALUES ('5swr945f8d9xpp64klbkfv6xr77bal6m','MjY1NjhlZDhiZWRjMjdkNDAxMjZiYzllMTg1NTM1NjBlMzVhNmI2Zjp7Imdvb2dsZS1vYXV0aDJfc3RhdGUiOiJkeGRiMVZmQW5pc0hjTU1EY3FxUTBTRFV6RDV3OTJJMiIsIm5leHQiOiIvIn0=','2016-01-15 04:59:07.737614');
INSERT INTO `django_session` VALUES ('kf5nslqvl8g8hx1nyw83zn1ukdts7roz','OWJlNWUzODM2ZTQyZmMzMGI0MThiY2ZhY2I1ZjY0YzI2YWNiNzdkYTp7fQ==','2016-01-15 05:46:08.840047');
CREATE TABLE "django_content_type" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(100) NOT NULL,
    "app_label" varchar(100) NOT NULL,
    "model" varchar(100) NOT NULL,
    UNIQUE ("app_label", "model")
);
INSERT INTO `django_content_type` VALUES (1,'permission','auth','permission');
INSERT INTO `django_content_type` VALUES (2,'group','auth','group');
INSERT INTO `django_content_type` VALUES (3,'user','auth','user');
INSERT INTO `django_content_type` VALUES (4,'content type','contenttypes','contenttype');
INSERT INTO `django_content_type` VALUES (5,'session','sessions','session');
INSERT INTO `django_content_type` VALUES (6,'site','sites','site');
INSERT INTO `django_content_type` VALUES (7,'log entry','admin','logentry');
INSERT INTO `django_content_type` VALUES (8,'school','treasure','school');
INSERT INTO `django_content_type` VALUES (9,'hub','treasure','hub');
INSERT INTO `django_content_type` VALUES (10,'teacher','treasure','teacher');
INSERT INTO `django_content_type` VALUES (11,'tag','treasure','tag');
INSERT INTO `django_content_type` VALUES (12,'pack','treasure','pack');
INSERT INTO `django_content_type` VALUES (13,'resource','treasure','resource');
INSERT INTO `django_content_type` VALUES (14,'files resource','treasure','filesresource');
INSERT INTO `django_content_type` VALUES (15,'web resource','treasure','webresource');
INSERT INTO `django_content_type` VALUES (16,'teacher downloads resource','treasure','teacherdownloadsresource');
INSERT INTO `django_content_type` VALUES (18,'teacher rates resource','treasure','teacherratesresource');
INSERT INTO `django_content_type` VALUES (19,'teacher wantsto talk resource','treasure','teacherwantstotalkresource');
INSERT INTO `django_content_type` VALUES (20,'user social auth','default','usersocialauth');
INSERT INTO `django_content_type` VALUES (21,'nonce','default','nonce');
INSERT INTO `django_content_type` VALUES (22,'association','default','association');
INSERT INTO `django_content_type` VALUES (23,'code','default','code');
INSERT INTO `django_content_type` VALUES (24,'poi','treasure','poi');
CREATE TABLE "django_admin_log" (
    "id" integer NOT NULL PRIMARY KEY,
    "action_time" datetime NOT NULL,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "content_type_id" integer REFERENCES "django_content_type" ("id"),
    "object_id" text,
    "object_repr" varchar(200) NOT NULL,
    "action_flag" smallint unsigned NOT NULL,
    "change_message" text NOT NULL
);
INSERT INTO `django_admin_log` VALUES (1,'2015-12-13 05:30:53.358000',1,8,'1','Clydebank High School',1,'');
INSERT INTO `django_admin_log` VALUES (2,'2015-12-13 05:31:11.487000',1,8,'2','St Peter the Apostle',1,'');
INSERT INTO `django_admin_log` VALUES (3,'2015-12-13 05:31:29.638000',1,9,'1','Southern Hub',1,'');
INSERT INTO `django_admin_log` VALUES (4,'2015-12-13 05:31:44.593000',1,9,'2','Northern Hub',1,'');
INSERT INTO `django_admin_log` VALUES (5,'2015-12-13 05:31:57.269000',1,11,'1','National 5',1,'');
INSERT INTO `django_admin_log` VALUES (6,'2015-12-13 05:32:04.561000',1,11,'2','National 4',1,'');
INSERT INTO `django_admin_log` VALUES (7,'2015-12-13 05:32:10.952000',1,11,'3','Higher',1,'');
INSERT INTO `django_admin_log` VALUES (8,'2015-12-13 05:32:19.653000',1,11,'4','Advanced Higher',1,'');
INSERT INTO `django_admin_log` VALUES (9,'2015-12-13 05:32:31.443000',1,11,'5','Information Systems',1,'');
INSERT INTO `django_admin_log` VALUES (10,'2015-12-13 05:32:38.981000',1,11,'6','Programming',1,'');
INSERT INTO `django_admin_log` VALUES (11,'2015-12-13 05:32:45.803000',1,11,'7','Java',1,'');
INSERT INTO `django_admin_log` VALUES (12,'2015-12-13 05:32:53.361000',1,11,'8','Python',1,'');
INSERT INTO `django_admin_log` VALUES (13,'2015-12-13 05:33:39.819000',1,10,'1','Billy Connolly',1,'');
INSERT INTO `django_admin_log` VALUES (14,'2015-12-13 05:38:44.322000',1,13,'1','Project Euler',3,'');
INSERT INTO `django_admin_log` VALUES (15,'2015-12-13 06:26:34.152000',1,12,'1','Project Euler',1,'');
INSERT INTO `django_admin_log` VALUES (16,'2015-12-13 06:27:25.072000',1,13,'2','Project Euler',2,'Changed tree and packs.');
INSERT INTO `django_admin_log` VALUES (17,'2015-12-13 06:55:35.728000',1,13,'3','Python Website',2,'Changed tree.');
INSERT INTO `django_admin_log` VALUES (18,'2015-12-13 06:55:44.417000',1,13,'2','Project Euler',2,'Changed tree.');
INSERT INTO `django_admin_log` VALUES (19,'2015-12-13 07:26:31.063000',1,13,'5','Project EUler Improved',1,'');
INSERT INTO `django_admin_log` VALUES (20,'2015-12-14 10:53:29.185220',1,13,'11','Python',2,'Changed tree and tags.');
INSERT INTO `django_admin_log` VALUES (21,'2015-12-14 10:53:49.130619',1,13,'10','Java',2,'Changed tree and tags.');
INSERT INTO `django_admin_log` VALUES (22,'2015-12-14 10:54:33.711703',1,13,'9','Cyber Security',2,'Changed tree and tags.');
INSERT INTO `django_admin_log` VALUES (23,'2015-12-14 10:54:41.490280',1,13,'8','HTML 101',2,'Changed tree and tags.');
INSERT INTO `django_admin_log` VALUES (24,'2015-12-14 10:54:56.153559',1,13,'7','CT 101 Homework',2,'Changed tree and tags.');
INSERT INTO `django_admin_log` VALUES (25,'2015-12-14 10:55:08.690544',1,13,'6','CT 101',2,'Changed tree and tags.');
INSERT INTO `django_admin_log` VALUES (26,'2015-12-14 10:55:16.139428',1,13,'5','Project EUler Improved',2,'No fields changed.');
INSERT INTO `django_admin_log` VALUES (27,'2015-12-14 10:55:20.625627',1,13,'4','Java Website',2,'No fields changed.');
INSERT INTO `django_admin_log` VALUES (28,'2015-12-14 10:55:23.829713',1,13,'3','Python Website',2,'No fields changed.');
INSERT INTO `django_admin_log` VALUES (29,'2015-12-14 10:55:32.227619',1,13,'1','Databases 101',2,'Changed tree.');
CREATE TABLE "auth_user_user_permissions" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL,
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id"),
    UNIQUE ("user_id", "permission_id")
);
CREATE TABLE "auth_user_groups" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL,
    "group_id" integer NOT NULL REFERENCES "auth_group" ("id"),
    UNIQUE ("user_id", "group_id")
);
CREATE TABLE "auth_user" (
    "id" integer NOT NULL PRIMARY KEY,
    "password" varchar(128) NOT NULL,
    "last_login" datetime NOT NULL,
    "is_superuser" bool NOT NULL,
    "username" varchar(30) NOT NULL UNIQUE,
    "first_name" varchar(30) NOT NULL,
    "last_name" varchar(30) NOT NULL,
    "email" varchar(75) NOT NULL,
    "is_staff" bool NOT NULL,
    "is_active" bool NOT NULL,
    "date_joined" datetime NOT NULL
);
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$10000$UPzKmOvX2dT7$EXWhkxl4ajYoDbLzh+TgZMWOfRN5rNrzcdXEa+j7khA=','2015-12-30 03:52:02.894092',1,'user','','','',1,1,'2015-12-13 05:29:44.584000');
INSERT INTO `auth_user` VALUES (2,'pbkdf2_sha256$10000$qbb6XOVWKBND$LYYhDwFl5iPjlx++n0Ctyrl9zYnadE4xz2EpdkI1DTQ=','2015-12-16 11:52:04.902905',0,'scott','','','scot@hood.com',0,1,'2015-12-16 11:52:04.902963');
INSERT INTO `auth_user` VALUES (3,'pbkdf2_sha256$10000$QgNJqDmd1MeG$cKArdFguqeEjZGmSJCTXPWFbgk0IfUH2oQWd7PZ+Rsc=','2015-12-16 11:52:19.329829',0,'hood','','','scot@hood.com',0,1,'2015-12-16 11:52:19.329888');
INSERT INTO `auth_user` VALUES (4,'pbkdf2_sha256$10000$MEHBipLmBE4F$5yQZFuUnq5Fr6CnNhNivjnbzBLUMBPu3q7npdPz8K/4=','2015-12-16 11:52:46.272334',0,'user2','','','iain@iain.com',0,1,'2015-12-16 11:52:46.272483');
INSERT INTO `auth_user` VALUES (5,'pbkdf2_sha256$10000$rkrrekRheAih$4kpprJQaZaPI41wfDwoTDVbs+Q3/Lo3jeOeHGt5F9Yc=','2016-01-01 05:07:25.341566',0,'quintin','','','quintin.cutts@glasgow.ac.uk',0,1,'2015-12-16 11:53:14.033757');
INSERT INTO `auth_user` VALUES (6,'pbkdf2_sha256$10000$xez2g0mtNnnj$GZt+hVwpgCVJIy085msBB1C6/6HCDjfaHBc/A1gS2oE=','2015-12-16 11:54:08.872405',0,'nigel','','','nrc@hsog.co.uk',0,1,'2015-12-16 11:53:44.567320');
INSERT INTO `auth_user` VALUES (7,'pbkdf2_sha256$10000$C7FicBUfvQ0h$Ig7sHSMLblXlRzJgChIIYe3ogp2x7S5AtXP4eQiLlxk=','2016-01-01 05:43:59.063630',0,'Brad','','','brad@pitt.org',0,1,'2016-01-01 05:43:59.063702');
CREATE TABLE "auth_permission" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(50) NOT NULL,
    "content_type_id" integer NOT NULL,
    "codename" varchar(100) NOT NULL,
    UNIQUE ("content_type_id", "codename")
);
INSERT INTO `auth_permission` VALUES (1,'Can add permission',1,'add_permission');
INSERT INTO `auth_permission` VALUES (2,'Can change permission',1,'change_permission');
INSERT INTO `auth_permission` VALUES (3,'Can delete permission',1,'delete_permission');
INSERT INTO `auth_permission` VALUES (4,'Can add group',2,'add_group');
INSERT INTO `auth_permission` VALUES (5,'Can change group',2,'change_group');
INSERT INTO `auth_permission` VALUES (6,'Can delete group',2,'delete_group');
INSERT INTO `auth_permission` VALUES (7,'Can add user',3,'add_user');
INSERT INTO `auth_permission` VALUES (8,'Can change user',3,'change_user');
INSERT INTO `auth_permission` VALUES (9,'Can delete user',3,'delete_user');
INSERT INTO `auth_permission` VALUES (10,'Can add content type',4,'add_contenttype');
INSERT INTO `auth_permission` VALUES (11,'Can change content type',4,'change_contenttype');
INSERT INTO `auth_permission` VALUES (12,'Can delete content type',4,'delete_contenttype');
INSERT INTO `auth_permission` VALUES (13,'Can add session',5,'add_session');
INSERT INTO `auth_permission` VALUES (14,'Can change session',5,'change_session');
INSERT INTO `auth_permission` VALUES (15,'Can delete session',5,'delete_session');
INSERT INTO `auth_permission` VALUES (16,'Can add site',6,'add_site');
INSERT INTO `auth_permission` VALUES (17,'Can change site',6,'change_site');
INSERT INTO `auth_permission` VALUES (18,'Can delete site',6,'delete_site');
INSERT INTO `auth_permission` VALUES (19,'Can add log entry',7,'add_logentry');
INSERT INTO `auth_permission` VALUES (20,'Can change log entry',7,'change_logentry');
INSERT INTO `auth_permission` VALUES (21,'Can delete log entry',7,'delete_logentry');
INSERT INTO `auth_permission` VALUES (22,'Can add school',8,'add_school');
INSERT INTO `auth_permission` VALUES (23,'Can change school',8,'change_school');
INSERT INTO `auth_permission` VALUES (24,'Can delete school',8,'delete_school');
INSERT INTO `auth_permission` VALUES (25,'Can add hub',9,'add_hub');
INSERT INTO `auth_permission` VALUES (26,'Can change hub',9,'change_hub');
INSERT INTO `auth_permission` VALUES (27,'Can delete hub',9,'delete_hub');
INSERT INTO `auth_permission` VALUES (28,'Can add teacher',10,'add_teacher');
INSERT INTO `auth_permission` VALUES (29,'Can change teacher',10,'change_teacher');
INSERT INTO `auth_permission` VALUES (30,'Can delete teacher',10,'delete_teacher');
INSERT INTO `auth_permission` VALUES (31,'Can add tag',11,'add_tag');
INSERT INTO `auth_permission` VALUES (32,'Can change tag',11,'change_tag');
INSERT INTO `auth_permission` VALUES (33,'Can delete tag',11,'delete_tag');
INSERT INTO `auth_permission` VALUES (34,'Can add pack',12,'add_pack');
INSERT INTO `auth_permission` VALUES (35,'Can change pack',12,'change_pack');
INSERT INTO `auth_permission` VALUES (36,'Can delete pack',12,'delete_pack');
INSERT INTO `auth_permission` VALUES (37,'Can add resource',13,'add_resource');
INSERT INTO `auth_permission` VALUES (38,'Can change resource',13,'change_resource');
INSERT INTO `auth_permission` VALUES (39,'Can delete resource',13,'delete_resource');
INSERT INTO `auth_permission` VALUES (40,'Can add files resource',14,'add_filesresource');
INSERT INTO `auth_permission` VALUES (41,'Can change files resource',14,'change_filesresource');
INSERT INTO `auth_permission` VALUES (42,'Can delete files resource',14,'delete_filesresource');
INSERT INTO `auth_permission` VALUES (43,'Can add web resource',15,'add_webresource');
INSERT INTO `auth_permission` VALUES (44,'Can change web resource',15,'change_webresource');
INSERT INTO `auth_permission` VALUES (45,'Can delete web resource',15,'delete_webresource');
INSERT INTO `auth_permission` VALUES (46,'Can add teacher downloads resource',16,'add_teacherdownloadsresource');
INSERT INTO `auth_permission` VALUES (47,'Can change teacher downloads resource',16,'change_teacherdownloadsresource');
INSERT INTO `auth_permission` VALUES (48,'Can delete teacher downloads resource',16,'delete_teacherdownloadsresource');
INSERT INTO `auth_permission` VALUES (52,'Can add teacher rates resource',18,'add_teacherratesresource');
INSERT INTO `auth_permission` VALUES (53,'Can change teacher rates resource',18,'change_teacherratesresource');
INSERT INTO `auth_permission` VALUES (54,'Can delete teacher rates resource',18,'delete_teacherratesresource');
INSERT INTO `auth_permission` VALUES (55,'Can add teacher wantsto talk resource',19,'add_teacherwantstotalkresource');
INSERT INTO `auth_permission` VALUES (56,'Can change teacher wantsto talk resource',19,'change_teacherwantstotalkresource');
INSERT INTO `auth_permission` VALUES (57,'Can delete teacher wantsto talk resource',19,'delete_teacherwantstotalkresource');
INSERT INTO `auth_permission` VALUES (58,'Can add user social auth',20,'add_usersocialauth');
INSERT INTO `auth_permission` VALUES (59,'Can change user social auth',20,'change_usersocialauth');
INSERT INTO `auth_permission` VALUES (60,'Can delete user social auth',20,'delete_usersocialauth');
INSERT INTO `auth_permission` VALUES (61,'Can add nonce',21,'add_nonce');
INSERT INTO `auth_permission` VALUES (62,'Can change nonce',21,'change_nonce');
INSERT INTO `auth_permission` VALUES (63,'Can delete nonce',21,'delete_nonce');
INSERT INTO `auth_permission` VALUES (64,'Can add association',22,'add_association');
INSERT INTO `auth_permission` VALUES (65,'Can change association',22,'change_association');
INSERT INTO `auth_permission` VALUES (66,'Can delete association',22,'delete_association');
INSERT INTO `auth_permission` VALUES (67,'Can add code',23,'add_code');
INSERT INTO `auth_permission` VALUES (68,'Can change code',23,'change_code');
INSERT INTO `auth_permission` VALUES (69,'Can delete code',23,'delete_code');
INSERT INTO `auth_permission` VALUES (70,'Can add poi',24,'add_poi');
INSERT INTO `auth_permission` VALUES (71,'Can change poi',24,'change_poi');
INSERT INTO `auth_permission` VALUES (72,'Can delete poi',24,'delete_poi');
CREATE TABLE "auth_group_permissions" (
    "id" integer NOT NULL PRIMARY KEY,
    "group_id" integer NOT NULL,
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id"),
    UNIQUE ("group_id", "permission_id")
);
CREATE TABLE "auth_group" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(80) NOT NULL UNIQUE
);
CREATE INDEX "treasure_teacherwantstotalkresource_c12e9d48" ON "treasure_teacherwantstotalkresource" ("teacher_id");
CREATE INDEX "treasure_teacherwantstotalkresource_217f3d22" ON "treasure_teacherwantstotalkresource" ("resource_id");
CREATE INDEX "treasure_teacherusesresource_c12e9d48" ON "treasure_teacherusesresource" ("teacher_id");
CREATE INDEX "treasure_teacherusesresource_25cd3720" ON "treasure_teacherusesresource" ("download_id");
CREATE INDEX "treasure_teacherusesresource_217f3d22" ON "treasure_teacherusesresource" ("resource_id");
CREATE INDEX "treasure_teacherratesresource_c12e9d48" ON "treasure_teacherratesresource" ("teacher_id");
CREATE INDEX "treasure_teacherratesresource_217f3d22" ON "treasure_teacherratesresource" ("resource_id");
CREATE INDEX "treasure_teacher_hubs_dbf6b7b7" ON "treasure_teacher_hubs" ("hub_id");
CREATE INDEX "treasure_teacher_hubs_c12e9d48" ON "treasure_teacher_hubs" ("teacher_id");
CREATE INDEX "treasure_teacher_abbc0ae2" ON "treasure_teacher" ("school_id");
CREATE INDEX "treasure_resource_tags_5659cca2" ON "treasure_resource_tags" ("tag_id");
CREATE INDEX "treasure_resource_tags_217f3d22" ON "treasure_resource_tags" ("resource_id");
CREATE INDEX "treasure_resource_packs_9391bab4" ON "treasure_resource_packs" ("pack_id");
CREATE INDEX "treasure_resource_packs_217f3d22" ON "treasure_resource_packs" ("resource_id");
CREATE INDEX "treasure_resource_e969df21" ON "treasure_resource" ("author_id")














;
CREATE INDEX "treasure_pack_tags_9391bab4" ON "treasure_pack_tags" ("pack_id");
CREATE INDEX "treasure_pack_tags_5659cca2" ON "treasure_pack_tags" ("tag_id");
CREATE INDEX "treasure_pack_e969df21" ON "treasure_pack" ("author_id")













;
CREATE INDEX "social_auth_usersocialauth_6340c63c" ON "social_auth_usersocialauth" ("user_id");
CREATE INDEX "social_auth_code_09bb5fb3" ON "social_auth_code" ("code");
CREATE INDEX "django_session_b7b81f0c" ON "django_session" ("expire_date");
CREATE INDEX "django_admin_log_6340c63c" ON "django_admin_log" ("user_id");
CREATE INDEX "django_admin_log_37ef4eb4" ON "django_admin_log" ("content_type_id");
CREATE INDEX "auth_user_user_permissions_83d7f98b" ON "auth_user_user_permissions" ("permission_id");
CREATE INDEX "auth_user_user_permissions_6340c63c" ON "auth_user_user_permissions" ("user_id");
CREATE INDEX "auth_user_groups_6340c63c" ON "auth_user_groups" ("user_id");
CREATE INDEX "auth_user_groups_5f412f9a" ON "auth_user_groups" ("group_id");
CREATE INDEX "auth_permission_37ef4eb4" ON "auth_permission" ("content_type_id");
CREATE INDEX "auth_group_permissions_83d7f98b" ON "auth_group_permissions" ("permission_id");
CREATE INDEX "auth_group_permissions_5f412f9a" ON "auth_group_permissions" ("group_id");
COMMIT;
