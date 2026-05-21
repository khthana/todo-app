---
name: context
description: Domain glossary for the Todo App project
metadata:
  type: project
---

# Todo App

Backend API สำหรับระบบ Task Management ที่รองรับ task หลายประเภท พร้อม dependencies และ state transitions

## Language

**Task**:
หน่วยงานที่ผู้ใช้ต้องการติดตามและดำเนินการให้เสร็จ มีได้หลายประเภทตาม behavior ที่แตกต่างกัน
_Avoid_: Todo, Item, Work

**StandardTask**:
Task พื้นฐานที่ไม่มี deadline หรือ recurrence — มีแค่ title, description, และ status
_Avoid_: SimpleTodo, BasicTask

**DeadlineTask**:
Task ที่ต้องเสร็จก่อนวันเวลาที่กำหนด มีแนวคิดเรื่อง overdue
_Avoid_: TimedTask, DueDateTask

**RecurringTask**:
Task ที่เมื่อ complete แล้วจะ spawn instance ใหม่โดยอัตโนมัติตาม recurrence pattern
_Avoid_: RepeatingTask, ScheduledTask

**SingleTableInheritance**:
กลยุทธ์การเก็บ Task hierarchy ใน database — ตาราง `tasks` เดียวรวมทุก type โดยใช้ `type` column เป็น discriminator columns ที่ไม่เกี่ยวกับ type นั้นจะเป็น NULL
_Avoid_: joined table, concrete table, polymorphic table

**TagManagement**:
Tags ถูกจัดการผ่าน Task endpoints โดยตรง — ส่ง tag names มาพร้อม task ระบบ auto-create tag ที่ยังไม่มี มี `GET /tags/` endpoint เดียวสำหรับ list tags ทั้งหมด ไม่มี POST/DELETE tags แยก
_Avoid_: tag CRUD, tag management API

**Overdue**:
สถานะ informational ของ DeadlineTask เมื่อเลย due_date แล้ว — ไม่ block การ complete task overdue เป็นข้อมูลให้ user รู้ว่าช้า แต่ยังสามารถ mark COMPLETED ได้ตามปกติ
_Avoid_: expired, late, past due

**StateTransition**:
การเปลี่ยน TaskStatus ที่อนุญาต: PENDING→IN_PROGRESS, PENDING→CANCELLED, IN_PROGRESS→COMPLETED, IN_PROGRESS→CANCELLED, IN_PROGRESS→PENDING การ transition ที่ห้าม: COMPLETED→anything, CANCELLED→anything (terminal states ทั้งคู่)
_Avoid_: status change, update status

**RecurrencePattern**:
Enum ที่กำหนดความถี่ของ RecurringTask มี 3 ค่า: `DAILY`, `WEEKLY`, `MONTHLY` — ใช้ Strategy Pattern เพื่อให้ extend เพิ่ม pattern ใหม่ได้โดยไม่แก้โค้ดเดิม
_Avoid_: cron, schedule, interval, frequency

**TaskService**:
Layer ที่รับผิดชอบ business logic ทั้งหมด — dependency checking, state transitions, spawning occurrences เรียกใช้ TaskRepository สำหรับ data access ไม่รู้จัก HTTP
_Avoid_: handler, controller, manager

**TaskRepository**:
Layer ที่รับผิดชอบ database operations เท่านั้น — query, save, delete ไม่มี business logic
_Avoid_: dao, store, database layer

**Tag**:
Entity ที่มี id เป็นของตัวเอง ใช้สำหรับจัดกลุ่ม Tasks — มีความสัมพันธ์แบบ many-to-many กับ Task (Task หนึ่งมีได้หลาย Tag, Tag หนึ่งใช้ได้กับหลาย Task) การแก้ชื่อ Tag จะกระทบทุก Task ที่ใช้ Tag นั้นพร้อมกัน
_Avoid_: label, category, keyword

**Occurrence**:
instance หนึ่งของ RecurringTask — เมื่อ complete แล้วระบบจะ spawn Occurrence ใหม่อัตโนมัติ โดย copy title, description, recurrence pattern, tags มาจากเดิม แต่ไม่ copy dependencies เพราะแต่ละ Occurrence เป็นอิสระ หากถึง end_recurrence_date แล้วจะไม่ spawn อีก
_Avoid_: instance, copy, clone

**Dependency**:
ความสัมพันธ์แบบ "blocked by" ระหว่าง Tasks — Task A depends on Task B หมายความว่า B ต้องเป็น `COMPLETED` ก่อน A จึงจะ complete ได้ Task ที่เป็น `CANCELLED` ไม่นับว่าเสร็จ ยังคง block Task ที่ขึ้นอยู่กับมันอยู่
_Avoid_: prerequisite, subtask, parent-child

**TaskStatus**:
Enum ที่แทน lifecycle ของ Task มี 4 ค่า: `PENDING` (รอดำเนินการ) → `IN_PROGRESS` (กำลังทำ) → `COMPLETED` (ทำเสร็จแล้ว) หรือ `CANCELLED` (ยกเลิก ไม่ทำแล้ว) Task ที่ถูก cancel ยังคงอยู่ใน database เพื่อ audit trail
_Avoid_: completed (boolean), done, finished
