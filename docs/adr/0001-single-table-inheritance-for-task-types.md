# Single Table Inheritance for Task Types

ระบบมี Task 3 ประเภท (StandardTask, DeadlineTask, RecurringTask) ที่สืบทอดจาก Task base class เราเลือกใช้ Single Table Inheritance (STI) โดยเก็บทุก type ในตาราง `tasks` ตารางเดียว พร้อม `type` column เป็น discriminator แทนที่จะแยกตาราง (Joined Table Inheritance) เพราะ Task types มีจำนวน columns ที่ต่างกันไม่มาก NULL overhead จึงน้อย และ query ทำได้โดยไม่ต้อง JOIN ทำให้โค้ดและ query เรียบง่ายกว่า

## Considered Options

- **STI (เลือก)** — ตารางเดียว, query ง่าย, NULL บางช่อง
- **Joined Table Inheritance** — ตารางแยกต่อ type, ไม่มี NULL, แต่ทุก query ต้อง JOIN
- **Concrete Table Inheritance** — ตารางแยกสมบูรณ์, query ง่ายต่อ type แต่ยากเมื่อต้องดู tasks ทุกประเภทรวมกัน
