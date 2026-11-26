#!/usr/bin/env python3
"""Auditor-inspired Coreboard V2.5 regression. Chrome simulates iPad size; not a device test."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,sys
URL="http://127.0.0.1:8123/coreboard-v2/"
KEY="qixun-coreboard-personal-v2"
CACHE="qixun-coreboard-v2-20261127-audit-rework-v25"
checks=[]
def ok(name,condition):
    assert condition,name
    checks.append(name)
def run():
  with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    for w,h in [(1194,834),(1024,768),(834,1194),(768,1024),(390,844)]:
      ctx=browser.new_context(viewport={"width":w,"height":h},has_touch=True)
      page=ctx.new_page(); errors=[]
      page.on("pageerror",lambda x:errors.append(str(x)))
      resp=page.goto(URL,wait_until="domcontentloaded")
      ok(f"{w} home 200",resp.status==200)
      now=page.locator('.now-card .task-card').first
      normal=page.locator('.lane[data-status="todo"] .task-card').nth(1)
      a=now.locator(".task-title").evaluate("(e)=>parseFloat(getComputedStyle(e).fontSize)")
      b=normal.locator(".task-title").evaluate("(e)=>parseFloat(getComputedStyle(e).fontSize)")
      ok(f"{w} Now enlarged title",a>b+2)
      a=now.bounding_box()["height"];b=normal.bounding_box()["height"]
      ok(f"{w} Now enlarged card",a>b+9)
      ok(f"{w} two lanes",page.locator(".lane").count()==2)
      page.locator('[data-advance="m1"]').last.click()
      ok(f"{w} progress",page.locator('.lane[data-status="done"] [data-card="m1"]').count()==1)
      page.locator('.lane[data-status="done"] [data-advance="m1"]').last.click()
      ok(f"{w} undo",page.locator('.lane[data-status="todo"] [data-card="m1"]').count()==1)
      page.locator('[data-tab="core"]').click()
      page.locator('[data-core-page="2"]').first.click()
      ok(f"{w} 77 words",page.locator('.core-cell').count()==77)
      c=page.locator(".core-scroll").evaluate("(e)=>({w:e.clientWidth,scroll:e.scrollWidth})")
      ok(f"{w} no full-grid horizontal overflow",c["scroll"]<=c["w"]+2)
      page.locator('[data-core-page="0"]').first.click()
      ok(f"{w} left page 42",page.locator(".core-cell").count()==42)
      page.locator('[data-core-page="1"]').first.click()
      ok(f"{w} right page 35",page.locator(".core-cell").count()==35)
      page.locator('[data-tab="choices"]').click()
      ok(f"{w} choices remain 2",page.locator(".choice-card").count()==2)
      page.locator('[data-tab="first"]').click()
      page.locator('[data-first-preset="tidy"]').click()
      ok(f"{w} Favourite play label","Favourite play" in page.locator('.big-step').nth(1).inner_text())
      page.locator('[data-first-say="play-favourite"]').click()
      page.wait_for_timeout(280)
      audio=page.locator("#voice-audio").evaluate("(e)=>({url:e.currentSrc,time:e.currentTime,err:e.error&&e.error.message})")
      ok(f"{w} correct MP3",audio["url"].endswith("first/play-favourite.mp3"))
      ok(f"{w} audio playing",audio["time"]>0 and not audio["err"])
      ok(f"{w} no JS exceptions",not errors)
      ctx.close()
    ctx=browser.new_context(viewport={"width":1024,"height":768},has_touch=True)
    page=ctx.new_page();page.goto(URL,wait_until="domcontentloaded")
    # Mouse/pointer drag across columns (browser simulation, not physical iPad).
    drag_handle=page.locator('[data-card="m3"] [data-drag="m3"]')
    drag_handle.scroll_into_view_if_needed()
    h=drag_handle.bounding_box();done=page.locator('.lane[data-status="done"]').bounding_box()
    x,y=h["x"]+h["width"]/2,h["y"]+h["height"]/2
    tx,ty=done["x"]+done["width"]/2,min(740,max(60,y))
    page.mouse.move(x,y);page.mouse.down();page.mouse.move(tx,ty,steps=13);page.mouse.up()
    ok("pointer drag to Done",page.locator('.lane[data-status="done"] [data-card="m3"]').count()==1)
    page.locator('.lane[data-status="done"] [data-advance="m3"]').last.click()
    ok("drag undo",page.locator('.lane[data-status="todo"] [data-card="m3"]').count()==1)
    page.reload(wait_until="domcontentloaded")
    ok("drag persistence",page.locator('.lane[data-status="todo"] [data-card="m3"]').count()==1)
    page.locator('a[href="./games/"]').click()
    ok("games unaffected",page.locator('[data-game]').count()==4)
    page.locator('a.back').click()
    # Simulate old data where the active card is NOT the first array item.
    page.locator('[data-advance="m1"]').last.click()
    page.evaluate("""key=>{
      const d=JSON.parse(localStorage.getItem(key));
      const cards=d.scenes.morning.cards;
      const active=cards.find(c=>c.id==='m3');const first=cards.find(c=>c.id==='m1');
      cards.splice(cards.indexOf(active),1);cards.splice(2,0,active);
      cards.forEach(x=>x.status=x.id==='m3'?'now':x.id==='m1'?'next':x.id==='m5'?'done':'next');
      d.routineTwoColumnMigration=false;
      d.photos=[{id:'legacy-photo',title:'照片',en:'Photo',image:'',allowed:true}];
      localStorage.setItem(key,JSON.stringify(d));
    }""",KEY)
    page.reload(wait_until="domcontentloaded")
    ok("legacy now migrated to top",page.locator(".now-card [data-card]").first.get_attribute("data-card")=="m3")
    ok("legacy photo retained",page.evaluate("k=>JSON.parse(localStorage.getItem(k)).photos.length",KEY)==1)
    page.locator('[data-advance="m3"]').last.click()
    stored=page.evaluate("k=>JSON.parse(localStorage.getItem(k))",KEY)
    ok("migration persisted",stored["routineTwoColumnMigration"]==True)
    ok("all old cards retained",len(set(x["id"] for x in stored["scenes"]["morning"]["cards"]))==5)
    # One remaining step must never claim the Then step is already completed.
    page.evaluate("""key=>{
      const d=JSON.parse(localStorage.getItem(key));
      d.scenes.morning.cards.forEach(x=>x.status=x.id==='m4'?'next':'done');
      localStorage.setItem(key,JSON.stringify(d));
    }""",KEY)
    page.reload(wait_until="domcontentloaded")
    ok("routine one-step THEN neutral","Choose a favourite activity" in page.locator(".focus-strip").inner_text())
    page.locator('[data-tab="first"]').click()
    ok("first-then one-step neutral","Choose a favourite activity" in page.locator(".firstthen").inner_text())
    # Cache + offline + one recording check.
    page.locator('[data-tab="core"]').click()
    page.wait_for_function("navigator.serviceWorker.controller!==null",timeout=30000)
    count=page.evaluate(f"async()=>{{const c=await caches.open('{CACHE}');return (await c.keys()).length}}")
    ok("new service-worker cache complete",count>=128)
    ctx.set_offline(True)
    page.reload(wait_until="domcontentloaded")
    page.locator('[data-tab="core"]').click()
    page.locator('[data-core="3-1"]').click()
    page.wait_for_timeout(250)
    ok("offline speech",page.locator("#voice-audio").evaluate("(e)=>e.currentTime>0"))
    ctx.close()
    # Static school PDF print: fresh context, reset target rings only through print CSS.
    ctx=browser.new_context(viewport={"width":1194,"height":834})
    page=ctx.new_page();page.goto(URL,wait_until="domcontentloaded")
    page.locator('[data-tab="core"]').click()
    page.locator('[data-core-page="2"]').first.click()
    page.emulate_media(media="print")
    rings=page.locator('.core-cell.target').first.evaluate("(e)=>({shadow:getComputedStyle(e).boxShadow,after:getComputedStyle(e,'::after').display})")
    ok("school printing removes target rings",rings["shadow"]=="none" and rings["after"]=="none")
    out=Path("coreboard-v2/print/qixun-coreboard-school-a3.pdf");out.parent.mkdir(parents=True,exist_ok=True)
    page.pdf(path=str(out),format="A3",landscape=True,print_background=True,margin={"top":"7mm","bottom":"7mm","left":"7mm","right":"7mm"})
    ok("PDF produced",out.stat().st_size>10000)
    browser.close()
  report={"total_pass":len(checks),"checks":checks,"status":"browser simulation only; physical iPad NOT TESTED"}
  evidence=Path("coreboard-v2/tests/v25-regression-results.json")
  evidence.parent.mkdir(parents=True,exist_ok=True)
  evidence.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
  print("REGRESSION_PASS",len(checks),"tests; result",evidence)
if __name__=="__main__":
    run()
