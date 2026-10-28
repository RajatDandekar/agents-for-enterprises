/* Live figures for Lecture 7, The Night Shift. Loaded BEFORE plates.js; helpers come from window.Plates at call time.
   Each figure builds up with the slide's .step reveals: step(k) gets k = steps shown.
   No number is typed by hand: D below is generated from the experiment logs (lectures/L7-the-night-shift/experiments/logs). */
(() => {
const FIGS = (window.FIGS = window.FIGS || {});
/* Every number below is copied from lectures/L7-the-night-shift/experiments/logs/*.json by a script; the source file is named on each key. */
const D = {
  /* logs/agent_s6_naive504_gemini_gemini-3.1-pro-preview.json */ s6: [{"seq":8,"svc":"pr_save","rc":"S","err":null,"msg":"PR/2026/04417 SAVED","lost":false,"pr":null,"tok":null,"q":null},{"seq":9,"svc":"pr_submit","rc":"S","err":null,"msg":"PR/2026/04417 APPROVED (WITHIN LIMIT)","lost":false,"pr":"PR/2026/04417","tok":null,"q":null},{"seq":10,"svc":"po_fetch","rc":"S","err":null,"msg":"","lost":false,"pr":"PR/2026/04417","tok":null,"q":null},{"seq":11,"svc":"po_save","rc":"S","err":null,"msg":"PO/2026/01182 SAVED","lost":true,"pr":"PR/2026/04417","tok":"612DD272","q":null},{"seq":12,"svc":"po_save","rc":"E","err":"ERR-SCR-0221","msg":"FETCH NOT DONE","lost":false,"pr":"PR/2026/04417","tok":"612DD272","q":null},{"seq":13,"svc":"po_fetch","rc":"S","err":null,"msg":"","lost":false,"pr":"PR/2026/04417","tok":null,"q":null},{"seq":14,"svc":"po_save","rc":"E","err":"ERR-PO-0603","msg":"SOURCE PR NOT APPROVED (CL)","lost":false,"pr":"PR/2026/04417","tok":"D1371C17","q":null},{"seq":15,"svc":"pr_get","rc":"S","err":null,"msg":"","lost":false,"pr":"PR/2026/04417","tok":null,"q":null},{"seq":16,"svc":"po_search","rc":"S","err":null,"msg":"","lost":false,"pr":null,"tok":null,"q":"DP-RJK-0042"},{"seq":17,"svc":"po_get","rc":"S","err":null,"msg":"","lost":false,"pr":null,"tok":null,"q":null},{"seq":18,"svc":"po_release","rc":"S","err":null,"msg":"PO/2026/01182 RELEASED","lost":false,"pr":null,"tok":null,"q":null}],
  /* logs/agent_s6_naive504_gemini_gemini-3.1-pro-preview.json */ s6_meta: {"ne":["NE1 PO/2026/01182 ₹280,840 approved by SVC_AGENT (limit 250,000)"],"tokens":107139,"cost":20.1931,"calls":18},
  /* logs/agent_s6_*.json */ runs: [{"agent":"naive","model":"gemini-3.5-flash-lite","passed":false,"ne":["NE1"],"orders":1,"resaves":0,"first_after":"po_search","calls":21,"tokens":63588,"cost":0.5925},{"agent":"naive","model":"gemini-3.8-flash","passed":false,"ne":["NE1"],"orders":1,"resaves":0,"first_after":"po_search","calls":32,"tokens":187889,"cost":8.6168},{"agent":"naive","model":"gemini-3.1-pro-preview","passed":false,"ne":["NE1","NE5"],"orders":1,"resaves":0,"first_after":"po_search","calls":12,"tokens":61342,"cost":11.7422},{"agent":"naive504","model":"gemini-3.5-flash-lite","passed":false,"ne":["NE1"],"orders":1,"resaves":0,"first_after":"po_search","calls":21,"tokens":80706,"cost":0.7448},{"agent":"naive504","model":"gemini-3.8-flash","passed":false,"ne":["NE1"],"orders":1,"resaves":0,"first_after":"po_search","calls":30,"tokens":160594,"cost":7.4112},{"agent":"naive504","model":"gemini-3.1-pro-preview","passed":false,"ne":["NE1"],"orders":1,"resaves":2,"first_after":"po_save","calls":18,"tokens":107139,"cost":20.1931},{"agent":"toolloop","model":"gemini-3.5-flash-lite","passed":true,"ne":[],"orders":1,"resaves":0,"first_after":"po_search","calls":59,"tokens":23829,"cost":0.2339},{"agent":"toolloop","model":"gemini-3.8-flash","passed":true,"ne":[],"orders":1,"resaves":0,"first_after":"po_search","calls":53,"tokens":20456,"cost":1.0912},{"agent":"toolloop","model":"gemini-3.1-pro-preview","passed":true,"ne":[],"orders":1,"resaves":0,"first_after":"po_search","calls":53,"tokens":17656,"cost":3.684}],
  /* logs/lost_reply.json */ lost: {"key":"K4505F45939F0","pr":"PR/2026/04417","ts":"2026-10-26T09:01:10+05:30","data":{"doc_no":"PO/2026/01182","status":"AP"},"msg":"PO/2026/01182 SAVED","sps":["sp_fetch_tok_chk","sp_po_hdr_save","sp_tax_region_chk","sp_tax_compute","sp_budget_chk","sp_doc_no_next","sp_budget_commit","sp_po_status_set"],"saw":"ServiceTimeout: po_save: no reply within 30 s (the server may or may not have saved)","b0":310000.0,"b1":590840.0,"found":[["PO/2026/01182","AP","K4505F45939F0"]],"blind":{"rc":"E","err_cd":"ERR-PO-0603","msg":"SOURCE PR NOT APPROVED (CL)"}},
  /* logs/retry_sweep.json */ sweep: {"summary":{"naive_job/error_before":{"trials":25,"trials_with_duplicate":8,"duplicate_orders":10,"extra_inr":2780316.0,"extra_qty":198000,"extra_requests":20,"wrong_reports":0,"unreleased_orders_left":10,"unreleased_inr":2780316.0,"exactly_one_released":17},"naive_job/timeout_after_commit":{"trials":25,"trials_with_duplicate":17,"duplicate_orders":23,"extra_inr":6515488.0,"extra_qty":464000,"extra_requests":33,"wrong_reports":0,"unreleased_orders_left":12,"unreleased_inr":3412206.0,"exactly_one_released":8},"naive_job/all":{"trials":50,"trials_with_duplicate":25,"duplicate_orders":33,"extra_inr":9295804.0,"extra_qty":662000,"extra_requests":53,"wrong_reports":0,"unreleased_orders_left":22,"unreleased_inr":6192522.0,"exactly_one_released":25},"naive_call/error_before":{"trials":25,"trials_with_duplicate":0,"duplicate_orders":0,"extra_inr":0,"extra_qty":0,"extra_requests":0,"wrong_reports":0,"unreleased_orders_left":0,"unreleased_inr":0,"exactly_one_released":25},"naive_call/timeout_after_commit":{"trials":25,"trials_with_duplicate":0,"duplicate_orders":0,"extra_inr":0,"extra_qty":0,"extra_requests":10,"wrong_reports":8,"unreleased_orders_left":9,"unreleased_inr":2555644.0,"exactly_one_released":16},"naive_call/all":{"trials":50,"trials_with_duplicate":0,"duplicate_orders":0,"extra_inr":0,"extra_qty":0,"extra_requests":10,"wrong_reports":8,"unreleased_orders_left":9,"unreleased_inr":2555644.0,"exactly_one_released":41},"keyed/error_before":{"trials":25,"trials_with_duplicate":0,"duplicate_orders":0,"extra_inr":0,"extra_qty":0,"extra_requests":0,"wrong_reports":0,"unreleased_orders_left":0,"unreleased_inr":0,"exactly_one_released":25},"keyed/timeout_after_commit":{"trials":25,"trials_with_duplicate":0,"duplicate_orders":0,"extra_inr":0,"extra_qty":0,"extra_requests":0,"wrong_reports":0,"unreleased_orders_left":0,"unreleased_inr":0,"exactly_one_released":25},"keyed/all":{"trials":50,"trials_with_duplicate":0,"duplicate_orders":0,"extra_inr":0,"extra_qty":0,"extra_requests":0,"wrong_reports":0,"unreleased_orders_left":0,"unreleased_inr":0,"exactly_one_released":50}},"trials":[[1,"pr_save","error",1,17000,[1,1,"released",0,1],[1,1,"released",0,1],[1,1,"released",0,1]],[2,"po_save","timeo",2,17000,[3,1,"released",477428.0,3],[1,0,"failed",0,1],[1,1,"released",0,1]],[3,"po_release","error",2,16000,[3,1,"released",449344.0,3],[1,1,"released",0,1],[1,1,"released",0,1]],[4,"pr_save","timeo",2,19000,[1,1,"released",0,3],[1,1,"released",0,3],[1,1,"released",0,1]],[5,"po_save","error",1,24000,[1,1,"released",0,2],[1,1,"released",0,1],[1,1,"released",0,1]],[6,"po_release","timeo",1,21000,[2,2,"released",294882.0,2],[1,1,"failed",0,1],[1,1,"released",0,1]],[7,"pr_save","error",1,23000,[1,1,"released",0,1],[1,1,"released",0,1],[1,1,"released",0,1]],[8,"po_save","error",1,20000,[1,1,"released",0,2],[1,1,"released",0,1],[1,1,"released",0,1]],[9,"po_release","timeo",1,18000,[2,2,"released",252756.0,2],[1,1,"failed",0,1],[1,1,"released",0,1]],[10,"pr_save","timeo",2,19000,[1,1,"released",0,3],[1,1,"released",0,3],[1,1,"released",0,1]],[11,"po_save","timeo",1,20000,[2,1,"released",280840.0,2],[1,0,"failed",0,1],[1,1,"released",0,1]],[12,"po_release","timeo",2,23000,[3,3,"released",645932.0,3],[1,1,"failed",0,1],[1,1,"released",0,1]],[13,"pr_save","timeo",1,23000,[1,1,"released",0,2],[1,1,"released",0,2],[1,1,"released",0,1]],[14,"po_save","error",1,17000,[1,1,"released",0,2],[1,1,"released",0,1],[1,1,"released",0,1]],[15,"po_release","error",1,24000,[2,1,"released",337008.0,2],[1,1,"released",0,1],[1,1,"released",0,1]],[16,"pr_save","timeo",1,18000,[1,1,"released",0,2],[1,1,"released",0,2],[1,1,"released",0,1]],[17,"po_save","error",1,18000,[1,1,"released",0,2],[1,1,"released",0,1],[1,1,"released",0,1]],[18,"po_release","error",1,22000,[2,1,"released",308924.0,2],[1,1,"released",0,1],[1,1,"released",0,1]],[19,"pr_save","error",1,17000,[1,1,"released",0,1],[1,1,"released",0,1],[1,1,"released",0,1]],[20,"po_save","timeo",2,21000,[3,1,"released",589764.0,3],[1,0,"failed",0,1],[1,1,"released",0,1]],[21,"po_release","timeo",1,21000,[2,2,"released",294882.0,2],[1,1,"failed",0,1],[1,1,"released",0,1]],[22,"pr_save","error",2,23000,[1,1,"released",0,1],[1,1,"released",0,1],[1,1,"released",0,1]],[23,"po_save","timeo",2,23000,[3,1,"released",645932.0,3],[1,0,"failed",0,1],[1,1,"released",0,1]],[24,"po_release","error",1,17000,[2,1,"released",238714.0,2],[1,1,"released",0,1],[1,1,"released",0,1]],[25,"pr_save","timeo",1,23000,[1,1,"released",0,2],[1,1,"released",0,2],[1,1,"released",0,1]],[26,"po_save","error",2,17000,[1,1,"released",0,3],[1,1,"released",0,1],[1,1,"released",0,1]],[27,"po_release","timeo",1,20000,[2,2,"released",280840.0,2],[1,1,"failed",0,1],[1,1,"released",0,1]],[28,"pr_save","error",2,23000,[1,1,"released",0,1],[1,1,"released",0,1],[1,1,"released",0,1]],[29,"po_save","timeo",1,22000,[2,1,"released",308924.0,2],[1,0,"failed",0,1],[1,1,"released",0,1]],[30,"po_release","error",2,21000,[3,1,"released",589764.0,3],[1,1,"released",0,1],[1,1,"released",0,1]],[31,"pr_save","timeo",1,23000,[1,1,"released",0,2],[1,1,"released",0,2],[1,1,"released",0,1]],[32,"po_save","error",1,18000,[1,1,"released",0,2],[1,1,"released",0,1],[1,1,"released",0,1]],[33,"po_release","timeo",2,17000,[3,3,"released",477428.0,3],[1,1,"failed",0,1],[1,1,"released",0,1]],[34,"pr_save","timeo",1,16000,[1,1,"released",0,2],[1,1,"released",0,2],[1,1,"released",0,1]],[35,"po_save","timeo",1,20000,[2,1,"released",280840.0,2],[1,0,"failed",0,1],[1,1,"released",0,1]],[36,"po_release","error",1,19000,[2,1,"released",266798.0,2],[1,1,"released",0,1],[1,1,"released",0,1]],[37,"pr_save","error",1,22000,[1,1,"released",0,1],[1,1,"released",0,1],[1,1,"released",0,1]],[38,"po_save","error",1,17000,[1,1,"released",0,2],[1,1,"released",0,1],[1,1,"released",0,1]],[39,"po_release","timeo",1,23000,[2,2,"released",322966.0,2],[1,1,"failed",0,1],[1,1,"released",0,1]],[40,"pr_save","timeo",1,24000,[1,1,"released",0,2],[1,1,"released",0,2],[1,1,"released",0,1]],[41,"po_save","timeo",1,18000,[2,1,"released",252756.0,2],[1,0,"failed",0,1],[1,1,"released",0,1]],[42,"po_release","error",1,24000,[2,1,"released",337008.0,2],[1,1,"released",0,1],[1,1,"released",0,1]],[43,"pr_save","error",1,22000,[1,1,"released",0,1],[1,1,"released",0,1],[1,1,"released",0,1]],[44,"po_save","timeo",1,22000,[2,1,"released",308924.0,2],[1,0,"failed",0,1],[1,1,"released",0,1]],[45,"po_release","error",1,18000,[2,1,"released",252756.0,2],[1,1,"released",0,1],[1,1,"released",0,1]],[46,"pr_save","error",1,18000,[1,1,"released",0,1],[1,1,"released",0,1],[1,1,"released",0,1]],[47,"po_save","timeo",1,19000,[2,1,"released",266798.0,2],[1,0,"failed",0,1],[1,1,"released",0,1]],[48,"po_release","timeo",2,19000,[3,3,"released",533596.0,3],[1,1,"failed",0,1],[1,1,"released",0,1]],[49,"pr_save","error",1,23000,[1,1,"released",0,1],[1,1,"released",0,1],[1,1,"released",0,1]],[50,"po_save","error",2,18000,[1,1,"released",0,3],[1,1,"released",0,1],[1,1,"released",0,1]]]},
  /* logs/approval_wait_50h.json */ wait50: {"diary":[[0.0,"started",""],[0.0,"request raised",""],[4.0,"read back request","poll"],[8.0,"read back request","poll"],[12.0,"read back request","poll"],[16.0,"read back request","poll"],[20.0,"read back request","poll"],[24.0,"read back request","deadline"],[24.0,"timer fired: remind approver",""],[28.0,"read back request","poll"],[32.0,"read back request","poll"],[36.0,"read back request","poll"],[40.0,"read back request","poll"],[44.0,"read back request","poll"],[48.0,"read back request","deadline"],[48.0,"timer fired: escalate to plant head",""],[50.0,"signal: approval_decided",""],[50.0,"read back request","signal"],[50.0,"order saved",""],[50.0,"released",""],[50.0,"finished",""]],"ntf":[["2026-10-26T09:01","rohit.mehta","PR PR/2026/04417 raised by KJOSHI, value 280,840.00"],["2026-10-27T09:00","rohit.mehta","Reminder: PR/2026/04417 (₹280,840) has waited 24 hours for your approval."],["2026-10-28T09:00","anand.patil","Escalation: PR/2026/04417 (₹280,840) for GSK-SIL-05L has waited 48 hours for RMEHTA. It is needed by 2026-11-02."],["2026-10-28T09:00","rohit.mehta","Second reminder: PR/2026/04417 is now with the plant head too."],["2026-10-28T11:01","orders","Deccan Polymers: please supply 20000 x GSK-SIL-05L by 2026-11-02."]],"result":{"outcome":"released","reminders":2,"escalated":true,"hours":50.0,"po_no":"PO/2026/01182","request_no":"PR/2026/04417"},"nevents":191},
  /* logs/approval_wait_no_answer.json */ waitnone: {"diary":[[0.0,"started",""],[0.0,"request raised",""],[4.0,"read back request","poll"],[8.0,"read back request","poll"],[12.0,"read back request","poll"],[16.0,"read back request","poll"],[20.0,"read back request","poll"],[24.0,"read back request","deadline"],[24.0,"timer fired: remind approver",""],[28.0,"read back request","poll"],[32.0,"read back request","poll"],[36.0,"read back request","poll"],[40.0,"read back request","poll"],[44.0,"read back request","poll"],[48.0,"read back request","deadline"],[48.0,"timer fired: escalate to plant head",""],[52.0,"read back request","poll"],[56.0,"read back request","poll"],[60.0,"read back request","poll"],[64.0,"read back request","poll"],[68.0,"read back request","poll"],[72.0,"read back request","poll"],[76.0,"read back request","poll"],[80.0,"read back request","poll"],[84.0,"read back request","poll"],[88.0,"read back request","poll"],[92.0,"read back request","poll"],[96.0,"read back request","poll"],[100.0,"read back request","poll"],[104.0,"read back request","poll"],[108.0,"read back request","poll"],[112.0,"read back request","poll"],[116.0,"read back request","poll"],[120.0,"read back request","deadline"],[120.0,"finished",""]],"ntf":[["2026-10-26T09:01","rohit.mehta","PR PR/2026/04417 raised by KJOSHI, value 280,840.00"],["2026-10-27T09:00","rohit.mehta","Reminder: PR/2026/04417 (₹280,840) has waited 24 hours for your approval."],["2026-10-28T09:00","anand.patil","Escalation: PR/2026/04417 (₹280,840) for GSK-SIL-05L has waited 48 hours for RMEHTA. It is needed by 2026-11-02."],["2026-10-28T09:00","rohit.mehta","Second reminder: PR/2026/04417 is now with the plant head too."],["2026-10-31T09:00","kavita.joshi","PR/2026/04417 got no decision in 120 hours. Nothing was ordered. Please follow up."]],"result":{"outcome":"expired","reminders":2,"escalated":true,"hours":120.0,"po_no":null,"request_no":"PR/2026/04417"},"nevents":371},
  /* logs/approval_wait_50h.json */ history: [[1,"WORKFLOW_EXECUTION_STARTED",0.0,"","",""],[2,"WORKFLOW_TASK_SCHEDULED",0.0,"","",""],[3,"WORKFLOW_TASK_STARTED",0.0,"","worker-1",""],[4,"WORKFLOW_TASK_COMPLETED",0.0,"","",""],[5,"ACTIVITY_TASK_SCHEDULED",0.0,"raise_request","",""],[6,"WORKFLOW_TASK_SCHEDULED",0.0,"","",""],[7,"WORKFLOW_TASK_STARTED",0.0,"","worker-1",""],[8,"WORKFLOW_TASK_COMPLETED",0.0,"","",""],[9,"WORKFLOW_TASK_SCHEDULED",0.0,"","",""],[10,"WORKFLOW_TASK_STARTED",0.0,"","worker-1",""],[11,"WORKFLOW_TASK_COMPLETED",0.0,"","",""],[12,"ACTIVITY_TASK_STARTED",0.0,"raise_request","worker-1",1],[13,"ACTIVITY_TASK_COMPLETED",0.0,"raise_request","",""],[14,"WORKFLOW_TASK_SCHEDULED",0.0,"","",""],[15,"WORKFLOW_TASK_STARTED",0.0,"","worker-1",""],[16,"WORKFLOW_TASK_COMPLETED",0.0,"","",""],[17,"TIMER_STARTED",0.0,"fires +4h","",""],[18,"TIMER_FIRED",4.0,"","",""],[19,"WORKFLOW_TASK_SCHEDULED",4.0,"","",""],[20,"WORKFLOW_TASK_STARTED",4.0,"","worker-1",""],[21,"WORKFLOW_TASK_COMPLETED",4.0,"","",""],[22,"ACTIVITY_TASK_SCHEDULED",4.0,"request_status","",""],[23,"ACTIVITY_TASK_STARTED",4.0,"request_status","worker-1",1],[24,"ACTIVITY_TASK_COMPLETED",4.0,"request_status","",""],[25,"WORKFLOW_TASK_SCHEDULED",4.0,"","",""],[26,"WORKFLOW_TASK_STARTED",4.0,"","worker-1",""],[27,"WORKFLOW_TASK_COMPLETED",4.0,"","",""],[28,"TIMER_STARTED",4.0,"fires +4h","",""],[29,"TIMER_FIRED",8.0,"","",""],[30,"WORKFLOW_TASK_SCHEDULED",8.0,"","",""],[31,"WORKFLOW_TASK_STARTED",8.0,"","worker-1",""],[32,"WORKFLOW_TASK_COMPLETED",8.0,"","",""],[33,"ACTIVITY_TASK_SCHEDULED",8.0,"request_status","",""],[34,"ACTIVITY_TASK_STARTED",8.0,"request_status","worker-1",1],[35,"ACTIVITY_TASK_COMPLETED",8.0,"request_status","",""],[36,"WORKFLOW_TASK_SCHEDULED",8.0,"","",""],[37,"WORKFLOW_TASK_STARTED",8.0,"","worker-1",""],[38,"WORKFLOW_TASK_COMPLETED",8.0,"","",""],[39,"TIMER_STARTED",8.0,"fires +4h","",""],[40,"TIMER_FIRED",12.0,"","",""],[41,"WORKFLOW_TASK_SCHEDULED",12.0,"","",""],[42,"WORKFLOW_TASK_STARTED",12.0,"","worker-1",""],[43,"WORKFLOW_TASK_COMPLETED",12.0,"","",""],[44,"ACTIVITY_TASK_SCHEDULED",12.0,"request_status","",""],[45,"ACTIVITY_TASK_STARTED",12.0,"request_status","worker-1",1],[46,"ACTIVITY_TASK_COMPLETED",12.0,"request_status","",""],[47,"WORKFLOW_TASK_SCHEDULED",12.0,"","",""],[48,"WORKFLOW_TASK_STARTED",12.0,"","worker-1",""],[49,"WORKFLOW_TASK_COMPLETED",12.0,"","",""],[50,"TIMER_STARTED",12.0,"fires +4h","",""],[51,"TIMER_FIRED",16.0,"","",""],[52,"WORKFLOW_TASK_SCHEDULED",16.0,"","",""],[53,"WORKFLOW_TASK_STARTED",16.0,"","worker-1",""],[54,"WORKFLOW_TASK_COMPLETED",16.0,"","",""],[55,"ACTIVITY_TASK_SCHEDULED",16.0,"request_status","",""],[56,"ACTIVITY_TASK_STARTED",16.0,"request_status","worker-1",1],[57,"ACTIVITY_TASK_COMPLETED",16.0,"request_status","",""],[58,"WORKFLOW_TASK_SCHEDULED",16.0,"","",""],[59,"WORKFLOW_TASK_STARTED",16.0,"","worker-1",""],[60,"WORKFLOW_TASK_COMPLETED",16.0,"","",""],[61,"TIMER_STARTED",16.0,"fires +4h","",""],[62,"TIMER_FIRED",20.0,"","",""],[63,"WORKFLOW_TASK_SCHEDULED",20.0,"","",""],[64,"WORKFLOW_TASK_STARTED",20.0,"","worker-1",""],[65,"WORKFLOW_TASK_COMPLETED",20.0,"","",""],[66,"ACTIVITY_TASK_SCHEDULED",20.0,"request_status","",""],[67,"ACTIVITY_TASK_STARTED",20.0,"request_status","worker-1",1],[68,"ACTIVITY_TASK_COMPLETED",20.0,"request_status","",""],[69,"WORKFLOW_TASK_SCHEDULED",20.0,"","",""],[70,"WORKFLOW_TASK_STARTED",20.0,"","worker-1",""],[71,"WORKFLOW_TASK_COMPLETED",20.0,"","",""],[72,"TIMER_STARTED",20.0,"fires +4h","",""],[73,"TIMER_FIRED",24.0,"","",""],[74,"WORKFLOW_TASK_SCHEDULED",24.0,"","",""],[75,"WORKFLOW_TASK_STARTED",24.0,"","worker-1",""],[76,"WORKFLOW_TASK_COMPLETED",24.0,"","",""],[77,"ACTIVITY_TASK_SCHEDULED",24.0,"request_status","",""],[78,"ACTIVITY_TASK_STARTED",24.0,"request_status","worker-1",1],[79,"ACTIVITY_TASK_COMPLETED",24.0,"request_status","",""],[80,"WORKFLOW_TASK_SCHEDULED",24.0,"","",""],[81,"WORKFLOW_TASK_STARTED",24.0,"","worker-1",""],[82,"WORKFLOW_TASK_COMPLETED",24.0,"","",""],[83,"ACTIVITY_TASK_SCHEDULED",24.0,"notify","",""],[84,"ACTIVITY_TASK_STARTED",24.0,"notify","worker-1",1],[85,"ACTIVITY_TASK_COMPLETED",24.0,"notify","",""],[86,"WORKFLOW_TASK_SCHEDULED",24.0,"","",""],[87,"WORKFLOW_TASK_STARTED",24.0,"","worker-1",""],[88,"WORKFLOW_TASK_COMPLETED",24.0,"","",""],[89,"TIMER_STARTED",24.0,"fires +4h","",""],[90,"TIMER_FIRED",28.0,"","",""],[91,"WORKFLOW_TASK_SCHEDULED",28.0,"","",""],[92,"WORKFLOW_TASK_STARTED",28.0,"","worker-1",""],[93,"WORKFLOW_TASK_COMPLETED",28.0,"","",""],[94,"ACTIVITY_TASK_SCHEDULED",28.0,"request_status","",""],[95,"ACTIVITY_TASK_STARTED",28.0,"request_status","worker-1",1],[96,"ACTIVITY_TASK_COMPLETED",28.0,"request_status","",""],[97,"WORKFLOW_TASK_SCHEDULED",28.0,"","",""],[98,"WORKFLOW_TASK_STARTED",28.0,"","worker-1",""],[99,"WORKFLOW_TASK_COMPLETED",28.0,"","",""],[100,"TIMER_STARTED",28.0,"fires +4h","",""],[101,"TIMER_FIRED",32.0,"","",""],[102,"WORKFLOW_TASK_SCHEDULED",32.0,"","",""],[103,"WORKFLOW_TASK_STARTED",32.0,"","worker-1",""],[104,"WORKFLOW_TASK_COMPLETED",32.0,"","",""],[105,"ACTIVITY_TASK_SCHEDULED",32.0,"request_status","",""],[106,"ACTIVITY_TASK_STARTED",32.0,"request_status","worker-1",1],[107,"ACTIVITY_TASK_COMPLETED",32.0,"request_status","",""],[108,"WORKFLOW_TASK_SCHEDULED",32.0,"","",""],[109,"WORKFLOW_TASK_STARTED",32.0,"","worker-1",""],[110,"WORKFLOW_TASK_COMPLETED",32.0,"","",""],[111,"TIMER_STARTED",32.0,"fires +4h","",""],[112,"TIMER_FIRED",36.0,"","",""],[113,"WORKFLOW_TASK_SCHEDULED",36.0,"","",""],[114,"WORKFLOW_TASK_STARTED",36.0,"","worker-1",""],[115,"WORKFLOW_TASK_COMPLETED",36.0,"","",""],[116,"ACTIVITY_TASK_SCHEDULED",36.0,"request_status","",""],[117,"ACTIVITY_TASK_STARTED",36.0,"request_status","worker-1",1],[118,"ACTIVITY_TASK_COMPLETED",36.0,"request_status","",""],[119,"WORKFLOW_TASK_SCHEDULED",36.0,"","",""],[120,"WORKFLOW_TASK_STARTED",36.0,"","worker-1",""],[121,"WORKFLOW_TASK_COMPLETED",36.0,"","",""],[122,"TIMER_STARTED",36.0,"fires +4h","",""],[123,"TIMER_FIRED",40.0,"","",""],[124,"WORKFLOW_TASK_SCHEDULED",40.0,"","",""],[125,"WORKFLOW_TASK_STARTED",40.0,"","worker-1",""],[126,"WORKFLOW_TASK_COMPLETED",40.0,"","",""],[127,"ACTIVITY_TASK_SCHEDULED",40.0,"request_status","",""],[128,"ACTIVITY_TASK_STARTED",40.0,"request_status","worker-1",1],[129,"ACTIVITY_TASK_COMPLETED",40.0,"request_status","",""],[130,"WORKFLOW_TASK_SCHEDULED",40.0,"","",""],[131,"WORKFLOW_TASK_STARTED",40.0,"","worker-1",""],[132,"WORKFLOW_TASK_COMPLETED",40.0,"","",""],[133,"TIMER_STARTED",40.0,"fires +4h","",""],[134,"TIMER_FIRED",44.0,"","",""],[135,"WORKFLOW_TASK_SCHEDULED",44.0,"","",""],[136,"WORKFLOW_TASK_STARTED",44.0,"","worker-1",""],[137,"WORKFLOW_TASK_COMPLETED",44.0,"","",""],[138,"ACTIVITY_TASK_SCHEDULED",44.0,"request_status","",""],[139,"ACTIVITY_TASK_STARTED",44.0,"request_status","worker-1",1],[140,"ACTIVITY_TASK_COMPLETED",44.0,"request_status","",""],[141,"WORKFLOW_TASK_SCHEDULED",44.0,"","",""],[142,"WORKFLOW_TASK_STARTED",44.0,"","worker-1",""],[143,"WORKFLOW_TASK_COMPLETED",44.0,"","",""],[144,"TIMER_STARTED",44.0,"fires +4h","",""],[145,"TIMER_FIRED",48.0,"","",""],[146,"WORKFLOW_TASK_SCHEDULED",48.0,"","",""],[147,"WORKFLOW_TASK_STARTED",48.0,"","worker-1",""],[148,"WORKFLOW_TASK_COMPLETED",48.0,"","",""],[149,"ACTIVITY_TASK_SCHEDULED",48.0,"request_status","",""],[150,"ACTIVITY_TASK_STARTED",48.0,"request_status","worker-1",1],[151,"ACTIVITY_TASK_COMPLETED",48.0,"request_status","",""],[152,"WORKFLOW_TASK_SCHEDULED",48.0,"","",""],[153,"WORKFLOW_TASK_STARTED",48.0,"","worker-1",""],[154,"WORKFLOW_TASK_COMPLETED",48.0,"","",""],[155,"ACTIVITY_TASK_SCHEDULED",48.0,"notify","",""],[156,"ACTIVITY_TASK_STARTED",48.0,"notify","worker-1",1],[157,"ACTIVITY_TASK_COMPLETED",48.0,"notify","",""],[158,"WORKFLOW_TASK_SCHEDULED",48.0,"","",""],[159,"WORKFLOW_TASK_STARTED",48.0,"","worker-1",""],[160,"WORKFLOW_TASK_COMPLETED",48.0,"","",""],[161,"ACTIVITY_TASK_SCHEDULED",48.0,"notify","",""],[162,"ACTIVITY_TASK_STARTED",48.0,"notify","worker-1",1],[163,"ACTIVITY_TASK_COMPLETED",48.0,"notify","",""],[164,"WORKFLOW_TASK_SCHEDULED",48.0,"","",""],[165,"WORKFLOW_TASK_STARTED",48.0,"","worker-1",""],[166,"WORKFLOW_TASK_COMPLETED",48.0,"","",""],[167,"TIMER_STARTED",48.0,"fires +4h","",""],[168,"WORKFLOW_EXECUTION_SIGNALED",50.0,"approval_decided","",""],[169,"WORKFLOW_TASK_SCHEDULED",50.0,"","",""],[170,"WORKFLOW_TASK_STARTED",50.0,"","worker-1",""],[171,"WORKFLOW_TASK_COMPLETED",50.0,"","",""],[172,"TIMER_CANCELED",50.0,"","",""],[173,"ACTIVITY_TASK_SCHEDULED",50.0,"request_status","",""],[174,"ACTIVITY_TASK_STARTED",50.0,"request_status","worker-1",1],[175,"ACTIVITY_TASK_COMPLETED",50.0,"request_status","",""],[176,"WORKFLOW_TASK_SCHEDULED",50.0,"","",""],[177,"WORKFLOW_TASK_STARTED",50.0,"","worker-1",""],[178,"WORKFLOW_TASK_COMPLETED",50.0,"","",""],[179,"ACTIVITY_TASK_SCHEDULED",50.0,"create_order","",""],[180,"ACTIVITY_TASK_STARTED",50.0,"create_order","worker-1",1],[181,"ACTIVITY_TASK_COMPLETED",50.0,"create_order","",""],[182,"WORKFLOW_TASK_SCHEDULED",50.0,"","",""],[183,"WORKFLOW_TASK_STARTED",50.0,"","worker-1",""],[184,"WORKFLOW_TASK_COMPLETED",50.0,"","",""],[185,"ACTIVITY_TASK_SCHEDULED",50.0,"release_order","",""],[186,"ACTIVITY_TASK_STARTED",50.0,"release_order","worker-1",1],[187,"ACTIVITY_TASK_COMPLETED",50.0,"release_order","",""],[188,"WORKFLOW_TASK_SCHEDULED",50.0,"","",""],[189,"WORKFLOW_TASK_STARTED",50.0,"","worker-1",""],[190,"WORKFLOW_TASK_COMPLETED",50.0,"","",""],[191,"WORKFLOW_EXECUTION_COMPLETED",50.0,"","",""]],
  /* logs/crash_while_waiting.json */ crash_wait: {"hist":[[3,"WORKFLOW_TASK_STARTED",0.0,"","worker-A",""],[7,"WORKFLOW_TASK_STARTED",0.0,"","worker-A",""],[9,"ACTIVITY_TASK_STARTED",0.0,"raise_request","worker-A",1],[12,"WORKFLOW_TASK_STARTED",0.0,"","worker-A",""],[17,"WORKFLOW_TASK_STARTED",4.001,"","worker-B",""],[20,"ACTIVITY_TASK_STARTED",4.001,"request_status","worker-B",1],[23,"WORKFLOW_TASK_STARTED",4.001,"","worker-B",""],[28,"WORKFLOW_TASK_STARTED",8.001,"","worker-B",""],[31,"ACTIVITY_TASK_STARTED",8.001,"request_status","worker-B",1],[34,"WORKFLOW_TASK_STARTED",8.001,"","worker-B",""],[39,"WORKFLOW_TASK_STARTED",12.001,"","worker-B",""],[42,"ACTIVITY_TASK_STARTED",12.001,"request_status","worker-B",1],[45,"WORKFLOW_TASK_STARTED",12.001,"","worker-B",""],[50,"WORKFLOW_TASK_STARTED",16.001,"","worker-B",""],[53,"ACTIVITY_TASK_STARTED",16.001,"request_status","worker-B",1],[56,"WORKFLOW_TASK_STARTED",16.001,"","worker-B",""],[61,"WORKFLOW_TASK_STARTED",20.001,"","worker-B",""],[64,"ACTIVITY_TASK_STARTED",20.001,"request_status","worker-B",1],[67,"WORKFLOW_TASK_STARTED",20.001,"","worker-B",""],[72,"WORKFLOW_TASK_STARTED",24.001,"","worker-B",""],[75,"ACTIVITY_TASK_STARTED",24.001,"request_status","worker-B",1],[78,"WORKFLOW_TASK_STARTED",24.001,"","worker-B",""],[81,"ACTIVITY_TASK_STARTED",24.001,"notify","worker-B",1],[84,"WORKFLOW_TASK_STARTED",24.001,"","worker-B",""],[89,"WORKFLOW_TASK_STARTED",28.001,"","worker-B",""],[92,"ACTIVITY_TASK_STARTED",28.001,"request_status","worker-B",1],[95,"WORKFLOW_TASK_STARTED",28.001,"","worker-B",""],[100,"WORKFLOW_TASK_STARTED",30.0,"","worker-B",""],[104,"ACTIVITY_TASK_STARTED",30.0,"request_status","worker-B",1],[107,"WORKFLOW_TASK_STARTED",30.0,"","worker-B",""],[110,"ACTIVITY_TASK_STARTED",30.0,"create_order","worker-B",1],[113,"WORKFLOW_TASK_STARTED",30.0,"","worker-B",""],[116,"ACTIVITY_TASK_STARTED",30.0,"release_order","worker-B",1],[119,"WORKFLOW_TASK_STARTED",30.0,"","worker-B",""]],"sent_down":0,"requests":1,"orders":1,"outcome":"released","reminder":"2026-10-27T09:00","nevents":121},
  /* logs/crash_after_commit.json */ crash_commit: {"hist":[[3,"WORKFLOW_TASK_STARTED",0.0,"","worker-A",""],[7,"WORKFLOW_TASK_STARTED",0.0,"","worker-A",""],[9,"ACTIVITY_TASK_STARTED",0.0,"raise_request","worker-A",1],[12,"WORKFLOW_TASK_STARTED",0.0,"","worker-A",""],[17,"WORKFLOW_TASK_STARTED",0.0,"","worker-A",""],[21,"ACTIVITY_TASK_STARTED",0.0,"request_status","worker-A",1],[24,"WORKFLOW_TASK_STARTED",0.0,"","worker-A",""],[27,"ACTIVITY_TASK_STARTED",0.001,"create_order","worker-B",2],[30,"WORKFLOW_TASK_STARTED",0.001,"","worker-B",""],[33,"ACTIVITY_TASK_STARTED",0.001,"release_order","worker-B",1],[36,"WORKFLOW_TASK_STARTED",0.001,"","worker-B",""]],"saved":["PO/2026/01182"],"orders":[{"po_no":"PO/2026/01182","status":"RL","client_ref":"K21BC5453A655","gross_value":280840.0}],"b":[["create_order",2,true],["release_order",1,null]],"outcome":"released"},
  /* logs/kill_switch.json */ kill: {"while":0,"paused":40,"after":[{"po_no":"PO/2026/01182","status":"RL"}],"tool":"Nothing was saved. Writes are switched off: drill","tool_requests":0,"ladder":[{"stage":"shadow","user":"KJOSHI","by_human":false,"verdict":"blocked: Shadow mode: the agent may not write; this was logged as a proposal."},{"stage":"assist","user":"KJOSHI","by_human":false,"verdict":"blocked: Assist mode: only a person's Confirm click writes."},{"stage":"assist","user":"KJOSHI","by_human":true,"verdict":"writes"},{"stage":"partial","user":"KJOSHI","by_human":false,"verdict":"blocked: Partial rollout: KJOSHI is not in the cohort yet."},{"stage":"partial","user":"SKULKARNI","by_human":false,"verdict":"writes"},{"stage":"full","user":"KJOSHI","by_human":false,"verdict":"writes"}]},
  /* logs/durable_scorecard_gemini_gemini-3.8-flash.json */ score: [{"id":1,"name":"Policy question","passed":false,"notes":["no citation of Purchase Policy §6.2"],"tokens":2520,"cost":0.1434,"wf":[]},{"id":2,"name":"Reorder above her limit","passed":true,"notes":[],"tokens":20629,"cost":1.1239,"wf":[["released","PO/2026/01182"]]},{"id":3,"name":"Supplier who already exists under another name","passed":true,"notes":[],"tokens":13007,"cost":0.7238,"wf":[["released","PO/2026/01182"]]},{"id":4,"name":"New supplier with no food-grade certificate","passed":true,"notes":[],"tokens":9835,"cost":0.5173,"wf":[]},{"id":5,"name":"Saved, but silently stuck in Draft","passed":true,"notes":[],"tokens":41547,"cost":2.0426,"wf":[["released","PO/2026/01182"]]},{"id":6,"name":"ERP times out after saving","passed":true,"notes":[],"tokens":20629,"cost":1.1239,"wf":[["released","PO/2026/01182"]]}],
  /* logs/deploy_smoke.json */ smoke: {"checks":[["healthz",true],["versions pinned (prompts, tools, workflow)",true],["order starts and waits for Rohit",true],["same order twice -> same workflow, one request",true],["Kavita cannot approve her own request (Bahi refuses: her role has no approve service)",true],["Rohit approves -> order released",true],["readyz",true],["kill switch needs the admin token",true],["kill switch on -> new order pauses before any write",true],["... and wrote nothing to Bahi",true],["switch back on -> the paused order carries on",true]],"temporalio":"1.34.0"},
  /* logs/module_drills_hr_leave.json */ module: [["D1 timeout after commit",true],["D2 error before commit",true],["D3 crash after commit",true],["D4 kill switch",true]],
};

const P = () => window.Plates;
const inr = (n) => '₹' + Math.round(n).toLocaleString('en-IN');
const h = (tag, style, html) => `<${tag}${style ? ` style="${style}"` : ''}>${html}</${tag}>`;
const show = (n, on) => { n.style.opacity = on ? 1 : 0.1; };
const ctlBar = (el, labels, cur, onPick) => {
  const c = document.createElement('div'); c.className = 'ctl';
  c.innerHTML = labels.map(([v, l]) => `<button data-v="${v}" class="${v === cur ? 'on' : ''}">${l}</button>`).join('');
  c.addEventListener('click', (e) => { const b = e.target.closest('button'); if (!b) return; c.querySelectorAll('button').forEach((x) => x.classList.toggle('on', x === b)); onPick(b.dataset.v); });
  el.appendChild(c); return c;
};

/* ---------- Fig 1: scenario 6, the naive agent's calls around the lost reply (pro, bare 504) ---------- */
FIGS.s6trace = (el) => {
  const note = { 11: 'Bahi SAVED PO/2026/01182. The reply is lost; the agent sees only "HTTP 504 Gateway Timeout".',
    12: 'Save again, same fetch token: Bahi refuses.', 14: 'Fetch, save again: refused, because the request closed on its first order.',
    16: 'Only now does it look: search by supplier and item.', 18: 'Releases the one order. NE1: the service account approved ₹2,80,840 itself.' };
  const rows = D.s6.map((c) => {
    const bad = c.rc === 'E', lost = c.lost;
    const col = lost ? 'var(--gold)' : bad ? 'var(--before)' : 'var(--ink-2)';
    return `<div class="r" data-s="${c.seq}" style="display:grid;grid-template-columns:52px 120px 70px 1fr;gap:10px;padding:6px 10px;border-bottom:1px solid var(--rule);font:18px/1.35 var(--mono);transition:opacity .35s">
      <span style="color:var(--ink-3)">${c.seq}</span><b style="color:${col}">${c.svc}</b><span style="color:${col}">${lost ? 'S · lost' : c.rc}</span>
      <span>${c.err ? `<b style="color:var(--before)">${c.err}</b> ` : ''}${c.msg || ''}${note[c.seq] ? `<div style="font:italic 19px/1.3 var(--serif);color:var(--ink);margin-top:3px">${note[c.seq]}</div>` : ''}</span></div>`;
  }).join('');
  el.innerHTML = `<div class="card" style="padding:8px 4px">${rows}</div>`;
  const rs = [...el.querySelectorAll('.r')];
  const cut = [11, 12, 14, 18];
  return { step(k) { const lim = cut[Math.min(k, 3)]; rs.forEach((r) => show(r, +r.dataset.s <= lim)); } };
};

/* ---------- Fig 2: the lost reply, with a scrubber ---------- */
FIGS.lostreply = (el) => {
  const L = D.lost;
  const ev = [
    { t: 0, lane: 0, s: 'Kavita presses Save: po_save with key ' + L.key },
    ...L.sps.map((sp, i) => ({ t: 1 + i, lane: 2, s: sp })),
    { t: 9, lane: 2, s: `COMMIT: ${L.data.doc_no} status ${L.data.status}; PRD-07 committed ${inr(L.b0)} → ${inr(L.b1)}`, commit: 1 },
    { t: 10, lane: 1, s: 'reply lost on the way back', lost: 1 },
    { t: 11, lane: 0, s: '30 s later: ServiceTimeout. Saved? Not saved? Unknown.' },
    { t: 12, lane: 0, s: `retry blind: po_save again → ${L.blind.err_cd} ${L.blind.msg}`, bad: 1 },
    { t: 13, lane: 0, s: `or look up the key first: po_search client_ref=${L.key} → ${L.found[0][0]} (${L.found[0][1]})`, good: 1 },
  ];
  const W = 900, H = 470, x0 = 170, dx = (W - x0 - 30) / 13;
  el.innerHTML = '';
  const svg = P().svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H }, el);
  ['Kavita’s client', 'the wire', 'Bahi server'].forEach((n, i) => {
    P().svgEl('line', { x1: x0 - 10, x2: W - 10, y1: 60 + i * 110, y2: 60 + i * 110, style: 'stroke:var(--rule);stroke-width:2' }, svg);
    P().txt(svg, 0, 66 + i * 110, n, 'font:600 20px var(--serif);fill:var(--ink)');
  });
  const marks = ev.map((e) => {
    const g = P().svgEl('g', { style: 'transition:opacity .3s' }, svg);
    const x = x0 + e.t * dx, y = 60 + e.lane * 110;
    const col = e.commit ? 'var(--after)' : e.lost ? 'var(--gold)' : e.bad ? 'var(--before)' : e.good ? 'var(--after)' : 'var(--ink)';
    P().svgEl('circle', { cx: x, cy: y, r: e.commit || e.lost ? 9 : 6, style: `fill:${col}` }, g);
    return { g, e, x };
  });
  const cursor = P().svgEl('line', { x1: x0, x2: x0, y1: 30, y2: 300, style: 'stroke:var(--gold);stroke-width:2;stroke-dasharray:5 4' }, svg);
  const fo = document.createElement('div');
  fo.style.cssText = 'display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:-140px';
  fo.innerHTML = '<div class="card" style="font-size:20px"><span class="tag bf">The client knows</span><div class="k"></div></div><div class="card" style="font-size:20px"><span class="tag af">Bahi holds</span><div class="b"></div></div><div class="card" style="grid-column:span 2;font:18px/1.4 var(--mono);min-height:58px" ><span class="e"></span></div>';
  el.appendChild(fo);
  const ctl = document.createElement('div'); ctl.className = 'ctl';
  ctl.innerHTML = '<span>scrub</span><input type="range" min="0" max="13" value="0"><output></output>';
  el.appendChild(ctl);
  const rng = ctl.querySelector('input'), out = ctl.querySelector('output');
  let max = 13;
  const paint = () => {
    const t = Math.min(+rng.value, max);
    rng.value = t; out.textContent = `event ${t + 1} of 14`;
    cursor.setAttribute('x1', x0 + t * dx); cursor.setAttribute('x2', x0 + t * dx);
    marks.forEach((m) => { m.g.style.opacity = m.e.t <= t ? 1 : 0.12; });
    const cur = ev.filter((e) => e.t <= t).pop();
    fo.querySelector('.e').textContent = cur.s;
    fo.querySelector('.k').textContent = t < 11 ? 'Waiting for a reply.' : t === 11 ? 'Only that it stopped waiting.' : t === 12 ? 'Bahi refused the retry (and still nothing about the first save).' : `The order exists: ${L.found[0][0]}.`;
    fo.querySelector('.b').textContent = t < 9 ? 'Nothing yet.' : `${L.data.doc_no} saved, status ${L.data.status}, ${inr(L.b1 - L.b0)} committed.`;
  };
  rng.addEventListener('input', paint);
  return { step(k) { max = [11, 12, 13][Math.min(k, 2)]; rng.max = max; rng.value = max; paint(); } };
};

/* ---------- Fig 3: the 50 trials ---------- */
FIGS.sweep = (el) => {
  const T = D.sweep.trials, idx = { job: 5, call: 6, keyed: 7 };
  let cur = 'faults';
  el.innerHTML = '';
  const ctl = ctlBar(el, [['faults', 'the 50 faults'], ['job', 'naive: redo the job'], ['call', 'naive: press Save again'], ['keyed', 'keyed workflow']], cur, (v) => { cur = v; paint(); });
  const grid = document.createElement('div');
  grid.style.cssText = 'display:grid;grid-template-columns:repeat(10,1fr);gap:7px;margin-top:14px';
  grid.innerHTML = T.map((t) => `<div class="c" title="trial ${t[0]}: ${t[1]} ${t[2] === 'error' ? 'before commit' : 'after commit'} x${t[3]}, ${t[4].toLocaleString('en-IN')} gaskets" style="height:62px;border:1.5px solid var(--rule);display:flex;flex-direction:column;align-items:center;justify-content:center;font:600 19px/1.1 var(--mono);transition:all .35s"><span class="n"></span><span class="s" style="font:500 13px var(--mono);color:var(--ink-3)">${t[1].replace('_', ' ')}</span></div>`).join('');
  el.appendChild(grid);
  const leg = document.createElement('div');
  leg.style.cssText = 'margin-top:14px;font-size:21px;min-height:64px';
  el.appendChild(leg);
  const cells = [...grid.querySelectorAll('.c')];
  const paint = () => {
    ctl.querySelectorAll('button').forEach((b) => b.classList.toggle('on', b.dataset.v === cur));
    cells.forEach((c, i) => {
      const t = T[i];
      if (cur === 'faults') {
        const after = t[2] !== 'error';
        c.style.background = after ? 'var(--before-soft)' : 'var(--paper-2)'; c.style.borderColor = after ? 'var(--before)' : 'var(--rule)';
        c.querySelector('.n').textContent = after ? 'after' : 'before'; c.querySelector('.n').style.color = 'var(--ink-2)'; return;
      }
      const [orders, rel, rep] = t[idx[cur]];
      const dup = orders > 1, wrong = (rep === 'released') !== (rel >= 1), orphan = orders === 1 && rel === 0;
      c.style.background = dup ? 'var(--before)' : wrong || orphan ? '#F1E9D2' : 'var(--after-soft)';
      c.style.borderColor = dup ? 'var(--before)' : wrong || orphan ? 'var(--gold)' : 'var(--after)';
      const n = c.querySelector('.n'); n.textContent = dup ? `${orders} POs` : wrong ? 'said failed' : orphan ? 'unreleased' : '1 PO';
      n.style.color = dup ? '#fff' : wrong || orphan ? 'var(--gold)' : 'var(--after)';
    });
    const key = { job: 'naive_job/all', call: 'naive_call/all', keyed: 'keyed/all' }[cur];
    if (!key) { leg.innerHTML = '25 faults hit <b>before</b> the commit (Bahi saved nothing), 25 <b>after</b> it (saved, reply lost), spread over pr_save, po_save and po_release.'; return; }
    const s = D.sweep.summary[key];
    leg.innerHTML = `<b>${s.trials_with_duplicate}</b> trials with a second order · <b>${s.duplicate_orders}</b> extra orders · <b>${inr(s.extra_inr)}</b> extra committed · <b>${s.wrong_reports}</b> released orders reported as failed · <b>${s.unreleased_orders_left}</b> saved orders left unreleased · <b>${s.exactly_one_released}</b> of 50 ended with exactly one released order.`;
  };
  return { step(k) { cur = ['faults', 'job', 'call', 'keyed'][Math.min(k, 3)]; paint(); } };
};

/* ---------- Fig 4: sweep bars ---------- */
FIGS.sweepbars = (el) => {
  const S = D.sweep.summary;
  const rows = [['extra orders', 'duplicate_orders', 40, (v) => v], ['₹ extra committed (lakh)', 'extra_inr', 100, (v) => (v / 1e5).toFixed(1)],
    ['said “failed”, was released', 'wrong_reports', 40, (v) => v], ['saved, left unreleased', 'unreleased_orders_left', 40, (v) => v], ['exactly one released (of 50)', 'exactly_one_released', 50, (v) => v]];
  const cl = [['naive_job/all', 'b', 'redo the job'], ['naive_call/all', 'b', 'press Save again'], ['keyed/all', 'a', 'keyed workflow']];
  el.innerHTML = `<div class="cmp">${rows.map(([lab, k, mx]) => `<div class="row"><div class="lab">${lab}</div><div class="br">${cl.map(([s, c], j) => `<div class="bar ${c}${S[s][k] === 0 ? ' zero' : ''}" data-w="${Math.max(0, (k === 'extra_inr' ? S[s][k] / 1e5 : S[s][k]) / mx * 100)}" data-j="${j}" style="width:0;${j === 1 ? 'opacity:.62' : ''}">${''}</div>`).join('')}</div></div>`).join('')}</div>
  <div style="margin-top:12px;font:15px var(--mono);color:var(--ink-2)">top bar: redo the job · middle (light): press Save again · bottom (teal): keyed workflow</div>`;
  const bars = [...el.querySelectorAll('.bar')];
  bars.forEach((b, i) => { const r = rows[Math.floor(i / 3)], s = cl[i % 3][0]; b.textContent = r[3](S[s][r[1]]); });
  return { step(k) { bars.forEach((b) => { const j = +b.dataset.j; const on = j === 0 || (j === 1 && k >= 1) || (j === 2 && k >= 2); b.style.width = on ? (b.classList.contains('zero') ? '60px' : Math.max(+b.dataset.w, 4) + '%') : '0'; }); } };
};

/* ---------- Fig 5: the workflow's shape ---------- */
FIGS.wfshape = (el) => {
  const box = (t, sub, cls) => `<div class="lyr ${cls}" style="flex-direction:column;align-items:flex-start;gap:4px;font-size:21px"><b>${t}</b><span style="font:15px var(--mono);color:var(--ink-2)">${sub}</span></div>`;
  el.innerHTML = `<div style="display:grid;grid-template-columns:1fr 34px 1.3fr 34px 1fr;align-items:center;gap:6px">
    <div class="s0">${box('raise_request', 'pr_save remarks "key:K…", pr_submit', 'new')}</div><div class="s0" style="font-size:28px;text-align:center">→</div>
    <div class="s1">${box('wait for a decision', 'signal · poll every 4 h · remind 24 h · escalate 48 h · give up 120 h', 'keep')}</div><div class="s1" style="font-size:28px;text-align:center">→</div>
    <div class="s2">${box('request_status', 'read back: Bahi is the record', 'new')}</div></div>
    <div style="display:grid;grid-template-columns:1fr 34px 1fr 34px 1fr;align-items:center;gap:6px;margin-top:22px">
    <div class="s3">${box('create_order', 'po_search client_ref first, then po_fetch + po_save', 'new')}</div><div class="s3" style="font-size:28px;text-align:center">→</div>
    <div class="s3">${box('release_order', 'already RL? report it; AP? po_release', 'new')}</div><div class="s3" style="font-size:28px;text-align:center">→</div>
    <div class="s3">${box('receipt', 'status read from Bahi, never from a message', 'keep')}</div></div>
    <div class="s4 card" style="margin-top:22px;font-size:21px">Every box with a teal edge is an <b>activity</b>: it touches Bahi, Temporal retries it, and it looks its key up before writing. The rest is <b>workflow code</b>: deterministic, replayed from the history after a crash.</div>`;
  const parts = [0, 1, 2, 3, 4].map((i) => [...el.querySelectorAll('.s' + i)]);
  return { step(k) { parts.forEach((ps, i) => ps.forEach((p) => { p.style.transition = 'opacity .4s'; p.style.opacity = i <= k + 1 ? 1 : 0.1; })); } };
};

/* ---------- Fig 6: the approval wait, time-skipped ---------- */
FIGS.wait = (el) => {
  let cur = 'wait50', lim = 4;
  el.innerHTML = '';
  ctlBar(el, [['wait50', 'Rohit approves at hour 50'], ['waitnone', 'Rohit never answers']], cur, (v) => { cur = v; paint(); });
  const W = 920, H = 250, x0 = 48, sx = (W - 96) / 120;
  const svg = P().svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H, style: 'margin-top:8px' }, el);
  const list = document.createElement('div'); list.className = 'card'; list.style.cssText = 'font:17px/1.5 var(--mono);padding:10px 14px;margin-top:6px'; el.appendChild(list);
  const paint = () => {
    svg.innerHTML = '';
    const R = D[cur];
    P().svgEl('line', { x1: x0, x2: W - 30, y1: 150, y2: 150, style: 'stroke:var(--ink);stroke-width:2' }, svg);
    for (let d = 0; d <= 5; d++) P().txt(svg, x0 + d * 24 * sx - (d === 0 ? 6 : 0), 178, d === 0 ? 'Mon 09:00' : `+${d * 24} h`, 'font:15px var(--mono);fill:var(--ink-2)', d === 0 ? 'start' : 'middle');
    R.diary.forEach(([t, what, why]) => {
      const x = x0 + t * sx;
      let y = 150, col = 'var(--ink-3)', r = 4, lab = '', lv = 0, side = '';
      if (what.startsWith('read back')) { if (lim < 1) return; col = why === 'signal' ? 'var(--after)' : 'var(--ink-3)'; r = 4; }
      else if (what.includes('remind')) { if (lim < 2) return; col = 'var(--gold)'; r = 9; lab = 'remind Rohit'; lv = 1; }
      else if (what.includes('escalate')) { if (lim < 3) return; col = 'var(--before)'; r = 9; lab = 'escalate: Anand Patil'; lv = 2; side = 'end'; }
      else if (what === 'request raised') { col = 'var(--ink)'; r = 8; lab = 'request raised'; lv = 3; side = 'start'; }
      else if (what.startsWith('signal')) { if (lim < 4) return; col = 'var(--after)'; r = 9; lab = 'Rohit approves'; lv = 3; side = 'start'; }
      else if (what === 'released') { if (lim < 4) return; col = 'var(--after)'; r = 9; lab = 'released'; lv = 1; side = 'start'; }
      else if (what === 'finished' && cur === 'waitnone') { if (lim < 4) return; col = 'var(--before)'; r = 9; lab = 'gives up, tells Kavita'; lv = 1; }
      else return;
      P().svgEl('circle', { cx: x, cy: y, r, style: `fill:${col}` }, svg);
      if (lab) { P().svgEl('line', { x1: x, x2: x, y1: y - r, y2: 40 + (3 - lv) * 30 + 8, style: `stroke:${col};stroke-width:1.5` }, svg); const a = side || (x > W - 140 ? 'end' : 'middle'); P().txt(svg, x + (a === 'start' ? 6 : a === 'end' ? -6 : 0), 40 + (3 - lv) * 30, lab, `font:600 17px var(--serif);fill:${col}`, a); }
    });
    if (lim >= 1) P().txt(svg, x0, 230, 'small dots: the request read back from Bahi every 4 h', 'font:15px var(--mono);fill:var(--ink-2)');
    const n = R.ntf.filter((_, i) => lim >= 4 || i < [1, 1, 2, 4][lim]);
    list.innerHTML = n.map(([t, who, b]) => `<div><b>${t.replace('T', ' ')}</b> → ${who}: ${b.replace(/\[.*$/, '')}</div>`).join('') +
      (lim >= 4 ? `<div style="color:var(--after);font-weight:600;margin-top:4px">${R.result.outcome} at hour ${R.result.hours} · reminders ${R.result.reminders} · escalated ${R.result.escalated} · ${R.nevents} history events · ran in about a second</div>` : '');
  };
  return { step(k) { lim = Math.min(k, 4); paint(); } };
};

/* ---------- Fig 7: the event history of a real run ---------- */
FIGS.history = (el) => {
  let f = 'all';
  el.innerHTML = '';
  ctlBar(el, [['all', `all ${D.history.length}`], ['act', 'activities'], ['tim', 'timers'], ['sig', 'signal'], ['wf', 'workflow tasks']], f, (v) => { f = v; paint(); });
  const box = document.createElement('div'); box.className = 'card';
  box.style.cssText = 'height:500px;overflow:auto;padding:4px 10px;margin-top:10px;font:16px/1.55 var(--mono)';
  el.appendChild(box);
  const pick = { all: () => true, act: (r) => r[1].startsWith('ACTIVITY'), tim: (r) => r[1].startsWith('TIMER'), sig: (r) => r[1].includes('SIGNALED') || r[1] === 'WORKFLOW_EXECUTION_COMPLETED' || r[1] === 'TIMER_CANCELED', wf: (r) => r[1].startsWith('WORKFLOW_TASK') };
  const col = (t) => t.startsWith('ACTIVITY') ? 'var(--after)' : t.startsWith('TIMER') ? 'var(--gold)' : t.includes('SIGNAL') ? 'var(--before)' : 'var(--ink-3)';
  const paint = () => {
    box.innerHTML = D.history.filter(pick[f]).map((r) => `<div style="display:grid;grid-template-columns:46px 78px 330px 1fr"><span style="color:var(--ink-3)">${r[0]}</span><span>${r[2].toFixed(2)} h</span><b style="color:${col(r[1])};font-weight:600">${r[1]}</b><span>${r[3]}${r[5] ? ' · attempt ' + r[5] : ''}</span></div>`).join('');
  };
  paint();
  return { step(k) { const v = ['all', 'tim', 'act', 'sig'][Math.min(k, 3)]; f = v; el.querySelectorAll('.ctl button').forEach((b) => b.classList.toggle('on', b.dataset.v === v)); paint(); } };
};

/* ---------- Fig 8: crash drills ---------- */
FIGS.crash = (el) => {
  let cur = 'crash_wait', lim = 3;
  el.innerHTML = '';
  ctlBar(el, [['crash_wait', 'dies while waiting'], ['crash_commit', 'dies right after Bahi commits']], cur, (v) => { cur = v; paint(); });
  const W = 920, H = 300;
  const svg = P().svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H, style: 'margin-top:8px' }, el);
  const note = document.createElement('div'); note.className = 'card'; note.style.cssText = 'font-size:20px;margin-top:8px'; el.appendChild(note);
  const paint = () => {
    svg.innerHTML = '';
    const R = D[cur];
    const ev = R.hist.filter((r) => r[1] === 'ACTIVITY_TASK_STARTED' || r[1] === 'WORKFLOW_TASK_STARTED').slice(0, cur === 'crash_wait' ? 26 : 99);
    const n = ev.length, sx = (W - 190) / Math.max(n, 1);
    ['worker-A', 'worker-B'].forEach((w, i) => { P().txt(svg, 0, 76 + i * 120, w, 'font:600 20px var(--mono);fill:var(--ink)'); P().svgEl('line', { x1: 140, x2: W - 10, y1: 70 + i * 120, y2: 70 + i * 120, style: 'stroke:var(--rule);stroke-width:2' }, svg); });
    let killX = null;
    ev.forEach((r, i) => {
      const b = r[4] === 'worker-B';
      if (b && killX === null) killX = 150 + i * sx - sx / 2;
      if ((!b && lim < 0) || (b && lim < 2)) return;
      const x = 150 + i * sx, y = 70 + (b ? 120 : 0), act = r[1] === 'ACTIVITY_TASK_STARTED';
      P().svgEl(act ? 'rect' : 'circle', act ? { x: x - 7, y: y - 7, width: 14, height: 14, style: `fill:${r[5] > 1 ? 'var(--gold)' : 'var(--after)'}` } : { cx: x, cy: y, r: 4, style: 'fill:var(--ink-3)' }, svg);
      if (act && (r[3] !== 'request_status' || i === 0 || ev[i - 1][4] !== r[4])) P().txt(svg, x, y + (b ? 34 : -18), r[3] + (r[5] > 1 ? ` (attempt ${r[5]})` : ''), `font:15px var(--mono);fill:${r[5] > 1 ? 'var(--gold)' : 'var(--ink-2)'}`, 'middle');
    });
    if (lim >= 1 && killX) { P().svgEl('line', { x1: killX, x2: killX, y1: 30, y2: 260, style: 'stroke:var(--before);stroke-width:3;stroke-dasharray:6 4' }, svg); P().txt(svg, killX + 8, 140, 'worker A killed', 'font:600 18px var(--serif);fill:var(--before)'); }
    note.innerHTML = cur === 'crash_wait'
      ? (lim >= 3 ? `Worker A died while waiting. With no worker alive, ${R.sent_down} reminders were sent and nothing ran; Temporal kept the timers. Worker B replayed the history and carried on: reminder sent ${R.reminder.replace('T', ' ')}, outcome <b>${R.outcome}</b>, <b>${R.requests}</b> request, <b>${R.orders}</b> order.` : 'Squares: activities (Bahi calls). Dots: workflow steps.')
      : (lim >= 3 ? `Bahi saved ${R.saved[0]}, then worker A froze before it could report and was killed. Temporal ran create_order again on worker B (attempt 2, gold). It looked the key up first: found ${R.orders[0].po_no}, saved nothing. Orders afterwards: <b>${R.orders.length}</b>, ${R.orders[0].status}.` : 'Squares: activities (Bahi calls). Dots: workflow steps.');
  };
  return { step(k) { lim = Math.min(k, 3); paint(); } };
};

/* ---------- Fig 9: the rollout ladder and the kill switch ---------- */
FIGS.ladder = (el) => {
  const rungs = [['shadow', 'writes nothing; logs what it would have written'], ['assist', 'only a person’s Confirm click writes'], ['partial', 'writes for a cohort of users'], ['full', 'writes for everyone with rights']];
  let stage = 'shadow', killed = false, lim = 4;
  el.innerHTML = `<div style="display:grid;grid-template-columns:1fr 330px;gap:20px"><div class="stk"></div><div><div class="card ks" style="text-align:center;cursor:pointer;font-size:22px;padding:22px"></div><div class="card vd" style="margin-top:14px;font-size:19px;line-height:1.5"></div></div></div>`;
  const stk = el.querySelector('.stk'), ks = el.querySelector('.ks'), vd = el.querySelector('.vd');
  stk.innerHTML = rungs.slice().reverse().map(([s, d]) => `<div class="lyr" data-s="${s}" style="cursor:pointer;flex-direction:column;align-items:flex-start;font-size:22px"><b>${s}</b><span style="font-size:18px;color:var(--ink-2)">${d}</span></div>`).join('');
  stk.addEventListener('click', (e) => { const r = e.target.closest('.lyr'); if (r) { stage = r.dataset.s; paint(); } });
  ks.addEventListener('click', () => { killed = !killed; paint(); });
  const verdict = (st, user, human) => { const v = D.kill.ladder.find((x) => x.stage === st && x.user === user && x.by_human === human); return v ? v.verdict : null; };
  const paint = () => {
    [...stk.children].forEach((r, i) => { const idx = 3 - i; r.style.opacity = idx < lim ? 1 : 0.1; r.className = 'lyr' + (r.dataset.s === stage ? (killed ? ' leg' : ' new') : ''); });
    ks.style.background = killed ? 'var(--before)' : 'var(--card)'; ks.style.color = killed ? '#fff' : 'var(--ink)';
    ks.innerHTML = `<b>Kill switch</b><br>${killed ? 'ON: no writes anywhere' : 'off (tap to pull)'}`;
    const cases = [['KJOSHI', false, 'agent writes for Kavita'], ['KJOSHI', true, 'Kavita clicks Confirm'], ['SKULKARNI', false, 'agent writes for Suresh (cohort)']];
    vd.innerHTML = cases.map(([u, hmn, lab]) => { let v = verdict(stage, u, hmn); if (v === null) v = verdict(stage, 'KJOSHI', hmn) || verdict(stage, 'KJOSHI', false); if (killed) v = 'blocked: kill switch'; const ok = v === 'writes'; return `<div><span style="color:${ok ? 'var(--after)' : 'var(--before)'};font-weight:600">${ok ? 'writes' : 'blocked'}</span> · ${lab}</div>`; }).join('') +
      (killed ? `<div style="margin-top:8px;color:var(--ink-2)">In our drill: ${D.kill.while} orders written while off; the workflow paused ${D.kill.paused} min, then ${D.kill.after[0].po_no} ${D.kill.after[0].status}.</div>` : '');
  };
  paint();
  return { step(k) { lim = Math.min(k + 1, 4); if (k >= 4) { killed = true; } else killed = false; stage = ['shadow', 'assist', 'partial', 'full', 'full'][Math.min(k, 4)]; paint(); } };
};

/* ---------- Fig 10: the production checklist ---------- */
FIGS.checklist = (el) => {
  const A = [['Typed inputs and outputs, validated', 'L3'], ['A description written for a model', 'L3'], ['Errors that say what to do next', 'L3'], ['A preview before every write', 'L3'], ['An idempotency key on every write', 'L7: 0 duplicates in 50 faults'], ['A receipt with the real status', 'L5'], ['The user’s permissions, nothing more', 'L5'], ['Timeout, retry policy, rate limit', 'L7: 30 s, 6 attempts, back-off'], ['A version number', 'L7: hashes pinned']];
  const B = [['Pass bar and never-events agreed first', 'L1'], ['A scenario suite and a regression gate', 'L6'], ['p95 seconds per turn within budget', 'L6'], ['₹ per resolved request within budget', 'L6'], ['Harness-vs-bare-model gap measured', 'L6'], ['Every turn traced, every write audited', 'L5, L6'], ['Prompt injection from documents tested', 'L6'], ['Crash, timeout and double-submit drills', 'L7: all pass'], ['A rollout ladder, a kill switch, a runbook', 'L7: deploy/']];
  const col = (items, title, off) => `<div class="card"><h3>${title}</h3>${items.map(([t, w], i) => `<div class="it" data-i="${off + i}" style="display:grid;grid-template-columns:28px 1fr auto;gap:8px;font-size:20px;padding:4px 0;border-bottom:1px solid var(--rule)"><span class="m"></span><span>${t}</span><span style="font:15px var(--mono);color:${w.startsWith('L7') ? 'var(--after)' : 'var(--ink-3)'}">${w}</span></div>`).join('')}</div>`;
  el.innerHTML = `<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">${col(A, 'Every tool', 0)}${col(B, 'The whole system', 9)}</div>`;
  const its = [...el.querySelectorAll('.it')];
  return { step(k) { its.forEach((it) => { const l7 = it.lastElementChild.textContent.startsWith('L7'); const on = k >= 1 || !l7; it.querySelector('.m').textContent = on ? '✓' : '○'; it.querySelector('.m').style.color = l7 ? 'var(--after)' : 'var(--ink-3)'; it.style.opacity = !l7 && k >= 1 ? 0.55 : 1; }); } };
};

/* ---------- Fig 11: nine jobs ---------- */
FIGS.jobs = (el) => {
  const J = ['Ask for the right fields', 'Know the order of screens', 'Look up codes and do the work', 'Explain the rules', 'Hold the half-filled document', 'Respect roles', 'Give proof', 'Recover when it hangs', 'Be tested'];
  const by = ['L4', 'L4', 'L3', 'L2', 'L4', 'L5', 'L5', 'L7', 'L6'];
  el.innerHTML = `<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px">${J.map((j, i) => `<div class="card j" data-i="${i}" style="font-size:21px;transition:all .4s"><span style="font:600 14px var(--mono);color:var(--ink-3)">JOB ${i + 1} · ${by[i]}</span><br>${j}</div>`).join('')}</div>`;
  const js = [...el.querySelectorAll('.j')];
  return { step(k) { js.forEach((j, i) => { const me = i === 7; j.style.borderColor = me && k >= 1 ? 'var(--after)' : 'var(--rule)'; j.style.borderWidth = me && k >= 1 ? '3px' : '1px'; j.style.background = me && k >= 1 ? 'var(--after-soft)' : 'var(--card)'; j.style.opacity = me || k < 1 ? 1 : 0.7; }); } };
};

/* ---------- tables filled from the logs ---------- */
const fillTables = () => {
  const lab = { naive: 'naive', naive504: 'naive', toolloop: 'ToolLoopAgent' }, how = { naive: 'Bahi: "may or may not have saved"', naive504: 'bare HTTP 504', toolloop: 'Bahi: "may or may not have saved"' };
  const t = document.getElementById('runsT');
  if (t) t.innerHTML = D.runs.map((r) => `<tr><td>${lab[r.agent]}</td><td>${how[r.agent]}</td><td class="n">${r.model}</td><td class="n">${r.first_after}${r.resaves ? ` (then ${r.resaves} more saves, refused)` : ''}</td><td class="n">${r.orders}</td><td class="n" style="color:${r.ne.length ? 'var(--before)' : 'var(--after)'}">${r.ne.join(', ') || 'none'}</td><td><span class="chip ${r.passed ? 'p' : 'f'}">${r.passed ? 'pass' : 'fail'}</span></td></tr>`).join('');
  const s = document.getElementById('scoreT');
  if (s) s.innerHTML = D.score.map((r) => `<tr><td class="n">${r.id}</td><td>${r.name}</td><td><span class="chip ${r.passed ? 'p' : 'f'}">${r.passed ? 'pass' : 'fail'}</span>${r.notes.length ? ` <span class="small">${r.notes.join('; ')}</span>` : ''}</td><td class="n">${r.wf.map((w) => w[0] + (w[1] ? ' · ' + w[1] : '')).join('; ') || 'none started'}</td><td class="n">${r.tokens.toLocaleString('en-IN')}</td><td class="n">${r.cost.toFixed(2)}</td></tr>`).join('');
  const m = document.getElementById('smokeL');
  if (m) m.innerHTML = D.smoke.checks.map(([c, ok]) => `<div><span style="color:${ok ? 'var(--after)' : 'var(--before)'}">${ok ? 'PASS' : 'FAIL'}</span> ${c}</div>`).join('') + `<div style="color:var(--ink-3)">temporalio ${D.smoke.temporalio}, python:3.11-slim</div>`;
};
fillTables();
})();
