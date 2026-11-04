# ARK Laptop Agent — Fixed Command Registry (v1, No LLM)

This is the command list for the small, fast, fixed-command laptop agent.
The agent only executes phrases in this file. Anything else gets the reply
'I do not recognise that command' and does nothing. That is intentional:
it is what keeps the agent fast, small, and safe without an LLM.

- **Voice and text share one parser.** A typed command and the same spoken
  command must produce the same action.
- **<text>, <number>, <website> and <file> are spoken variables**, not free
  prompts. Example: 'set volume to 50 percent' fills <number> with 50.
- **Risk: confirm** means the agent must ask 'Are you sure?' and wait for a
  clear yes before acting. Safe commands run immediately.
- **Custom ARK apps** (arkmedia, arksnap, arkdownload) are placeholders here:
  their real .exe paths go in the app registry when those apps are installed.
- **'Open notebook'** from the user's list is mapped to Jupyter Notebook.
  'INTELLIGI' is mapped to IntelliJ IDEA.

## Total commands: 418

### Apps

1. open chrome — action: launch_app | risk: safe
2. open edge — action: launch_app | risk: safe
3. open brave — action: launch_app | risk: safe
4. open firefox — action: launch_app | risk: safe
5. open opera — action: launch_app | risk: safe
6. open spotify — action: launch_app | risk: safe
7. open whatsapp — action: launch_app | risk: safe
8. open telegram — action: launch_app | risk: safe
9. open discord — action: launch_app | risk: safe
10. open zoom — action: launch_app | risk: safe
11. open microsoft teams — action: launch_app | risk: safe
12. open vlc media player — action: launch_app | risk: safe
13. open windows media player — action: launch_app | risk: safe
14. open photos — action: launch_app | risk: safe
15. open paint — action: launch_app | risk: safe
16. open notepad — action: launch_app | risk: safe
17. open calculator — action: launch_app | risk: safe
18. open calendar — action: launch_app | risk: safe
19. open clock — action: launch_app | risk: safe
20. open mail — action: launch_app | risk: safe
21. open snipping tool — action: launch_app | risk: safe
22. open file explorer — action: launch_app | risk: safe
23. open task manager — action: launch_app | risk: safe
24. open control panel — action: launch_app | risk: safe
25. open settings — action: launch_app | risk: safe
26. open windows security — action: launch_app | risk: safe
27. open arkmedia — action: launch_app | risk: safe
28. open arksnap — action: launch_app | risk: safe
29. open arkdownload — action: launch_app | risk: safe
30. open recycle bin — action: launch_app | risk: safe
31. open this pc — action: launch_app | risk: safe
32. open microsoft store — action: launch_app | risk: safe
33. open xbox — action: launch_app | risk: safe
### IDEs and Developer Tools

34. open visual studio code — action: launch_app | risk: safe
35. open visual studio — action: launch_app | risk: safe
36. open intellij idea — action: launch_app | risk: safe
37. open pycharm — action: launch_app | risk: safe
38. open webstorm — action: launch_app | risk: safe
39. open android studio — action: launch_app | risk: safe
40. open eclipse — action: launch_app | risk: safe
41. open netbeans — action: launch_app | risk: safe
42. open dev c++ — action: launch_app | risk: safe
43. open code blocks — action: launch_app | risk: safe
44. open sublime text — action: launch_app | risk: safe
45. open notepad++ — action: launch_app | risk: safe
46. open python interpreter — action: launch_app | risk: safe
47. open python idle — action: launch_app | risk: safe
48. open jupyter notebook — action: launch_app | risk: safe
49. open jupyter lab — action: launch_app | risk: safe
50. open anaconda navigator — action: launch_app | risk: safe
51. open git bash — action: launch_app | risk: safe
52. open command prompt — action: launch_app | risk: safe
53. open powershell — action: launch_app | risk: safe
54. open windows terminal — action: launch_app | risk: safe
55. open docker desktop — action: launch_app | risk: safe
56. open postman — action: launch_app | risk: safe
57. open mysql workbench — action: launch_app | risk: safe
58. open pgadmin — action: launch_app | risk: safe
59. open mongodb compass — action: launch_app | risk: safe
60. open figma — action: launch_app | risk: safe
61. open xampp — action: launch_app | risk: safe
62. open virtualbox — action: launch_app | risk: safe
63. open github desktop — action: launch_app | risk: safe
### Websites

64. open claude — action: open_website | risk: safe
65. open gemini — action: open_website | risk: safe
66. open grok — action: open_website | risk: safe
67. open chatgpt — action: open_website | risk: safe
68. open copilot — action: open_website | risk: safe
69. open youtube — action: open_website | risk: safe
70. open github — action: open_website | risk: safe
71. open google — action: open_website | risk: safe
72. open gmail — action: open_website | risk: safe
73. open google drive — action: open_website | risk: safe
74. open linkedin — action: open_website | risk: safe
75. open whatsapp web — action: open_website | risk: safe
76. open stack overflow — action: open_website | risk: safe
77. open wikipedia — action: open_website | risk: safe
78. open google docs — action: open_website | risk: safe
79. open google sheets — action: open_website | risk: safe
80. open notion — action: open_website | risk: safe
81. open netflix — action: open_website | risk: safe
82. open google maps — action: open_website | risk: safe
83. open google translate — action: open_website | risk: safe
84. open weather — action: open_website | risk: safe
85. open facebook — action: open_website | risk: safe
86. open instagram — action: open_website | risk: safe
87. open amazon — action: open_website | risk: safe
88. open daraz — action: open_website | risk: safe
89. open spotify web player — action: open_website | risk: safe
### System Settings

90. open system about — action: open_settings | risk: safe
91. open windows update — action: open_settings | risk: safe
92. open bluetooth settings — action: open_settings | risk: safe
93. open wifi settings — action: open_settings | risk: safe
94. open network settings — action: open_settings | risk: safe
95. open sound settings — action: open_settings | risk: safe
96. open display settings — action: open_settings | risk: safe
97. open brightness settings — action: open_settings | risk: safe
98. open personalization settings — action: open_settings | risk: safe
99. open theme settings — action: open_settings | risk: safe
100. open lock screen settings — action: open_settings | risk: safe
101. open accounts settings — action: open_settings | risk: safe
102. open privacy settings — action: open_settings | risk: safe
103. open storage settings — action: open_settings | risk: safe
104. open battery settings — action: open_settings | risk: safe
105. open power settings — action: open_settings | risk: safe
106. open date and time settings — action: open_settings | risk: safe
107. open language settings — action: open_settings | risk: safe
108. open keyboard settings — action: open_settings | risk: safe
109. open mouse settings — action: open_settings | risk: safe
110. open touchpad settings — action: open_settings | risk: safe
111. open printer settings — action: open_settings | risk: safe
112. open apps settings — action: open_settings | risk: safe
113. open default apps settings — action: open_settings | risk: safe
114. open startup apps settings — action: open_settings | risk: safe
115. open notifications settings — action: open_settings | risk: safe
116. open focus settings — action: open_settings | risk: safe
117. open accessibility settings — action: open_settings | risk: safe
118. open device manager — action: open_settings | risk: safe
119. open disk management — action: open_settings | risk: safe
120. open windows security and update — action: open_settings | risk: safe
### Files and Folders

121. open downloads folder — action: open_folder | risk: safe
122. open documents folder — action: open_folder | risk: safe
123. open pictures folder — action: open_folder | risk: safe
124. open videos folder — action: open_folder | risk: safe
125. open music folder — action: open_folder | risk: safe
126. open desktop folder — action: open_folder | risk: safe
### Close Apps

127. close chrome — action: close_app | risk: confirm
128. close edge — action: close_app | risk: confirm
129. close brave — action: close_app | risk: confirm
130. close firefox — action: close_app | risk: confirm
131. close spotify — action: close_app | risk: confirm
132. close whatsapp — action: close_app | risk: confirm
133. close telegram — action: close_app | risk: confirm
134. close discord — action: close_app | risk: confirm
135. close zoom — action: close_app | risk: confirm
136. close vlc media player — action: close_app | risk: confirm
137. close notepad — action: close_app | risk: confirm
138. close calculator — action: close_app | risk: confirm
139. close paint — action: close_app | risk: confirm
140. close file explorer — action: close_app | risk: confirm
141. close settings — action: close_app | risk: confirm
142. close task manager — action: close_app | risk: confirm
143. close microsoft word — action: close_app | risk: confirm
144. close microsoft excel — action: close_app | risk: confirm
145. close microsoft powerpoint — action: close_app | risk: confirm
146. close visual studio code — action: close_app | risk: confirm
147. close pycharm — action: close_app | risk: confirm
148. close intellij idea — action: close_app | risk: confirm
149. close android studio — action: close_app | risk: confirm
150. close microsoft teams — action: close_app | risk: confirm
151. close arkmedia — action: close_app | risk: confirm
152. close arksnap — action: close_app | risk: confirm
153. close arkdownload — action: close_app | risk: confirm
154. close current window — action: close_window | risk: confirm
155. close all browsers — action: close_all_browsers | risk: confirm
156. close all apps — action: close_all_apps | risk: confirm
### Browser Control

157. open new tab — action: open_new_tab | risk: safe
158. close tab — action: close_tab | risk: safe
159. close current tab — action: close_tab | risk: safe
160. reopen closed tab — action: reopen_tab | risk: safe
161. switch to next tab — action: next_tab | risk: safe
162. switch to previous tab — action: previous_tab | risk: safe
163. go to first tab — action: first_tab | risk: safe
164. go to last tab — action: last_tab | risk: safe
165. refresh page — action: refresh | risk: safe
166. hard refresh page — action: hard_refresh | risk: safe
167. go back — action: go_back | risk: safe
168. go forward — action: go_forward | risk: safe
169. go to home page — action: go_home | risk: safe
170. open new window — action: open_new_window | risk: safe
171. close browser window — action: close_window | risk: safe
172. open incognito window — action: open_private_window | risk: safe
173. open private window — action: open_private_window | risk: safe
174. open history — action: open_history | risk: safe
175. open downloads in browser — action: open_browser_downloads | risk: safe
176. open bookmarks — action: open_bookmarks | risk: safe
177. bookmark this page — action: bookmark_page | risk: safe
178. search for <text> — action: search_text | risk: safe
179. type <text> and press enter — action: type_and_enter | risk: safe
180. type <text> in search box and press enter — action: type_search_and_enter | risk: safe
181. open website <website> — action: open_website_typed | risk: safe
182. focus address bar — action: focus_address_bar | risk: safe
183. clear address bar — action: clear_address_bar | risk: safe
### Scrolling, Mouse and Keyboard

184. scroll down — action: scroll_down | risk: safe
185. scroll up — action: scroll_up | risk: safe
186. scroll down a little — action: scroll_down_small | risk: safe
187. scroll up a little — action: scroll_up_small | risk: safe
188. scroll down a lot — action: scroll_down_large | risk: safe
189. scroll up a lot — action: scroll_up_large | risk: safe
190. scroll to top of page — action: scroll_top | risk: safe
191. scroll to bottom of page — action: scroll_bottom | risk: safe
192. scroll right — action: scroll_right | risk: safe
193. scroll left — action: scroll_left | risk: safe
194. page down — action: page_down | risk: safe
195. page up — action: page_up | risk: safe
196. scroll down <number> times — action: scroll_down_n | risk: safe
197. scroll up <number> times — action: scroll_up_n | risk: safe
198. move mouse up — action: mouse_up | risk: safe
199. move mouse down — action: mouse_down | risk: safe
200. move mouse left — action: mouse_left | risk: safe
201. move mouse right — action: mouse_right | risk: safe
202. click — action: mouse_click | risk: safe
203. double click — action: mouse_double_click | risk: safe
204. right click — action: mouse_right_click | risk: safe
205. press enter — action: key_enter | risk: safe
206. press escape — action: key_escape | risk: safe
207. press tab — action: key_tab | risk: safe
208. press space — action: key_space | risk: safe
209. select all — action: key_select_all | risk: safe
210. copy — action: key_copy | risk: safe
211. paste — action: key_paste | risk: safe
212. cut — action: key_cut | risk: safe
213. undo — action: key_undo | risk: safe
214. redo — action: key_redo | risk: safe
### Volume, Media and Display

215. mute volume — action: mute | risk: safe
216. unmute volume — action: unmute | risk: safe
217. turn sound off — action: mute | risk: safe
218. turn sound on — action: unmute | risk: safe
219. volume up — action: volume_up | risk: safe
220. volume down — action: volume_down | risk: safe
221. increase volume — action: volume_up | risk: safe
222. decrease volume — action: volume_down | risk: safe
223. set volume to <number> percent — action: set_volume | risk: safe
224. set volume to <number> — action: set_volume | risk: safe
225. play — action: media_play | risk: safe
226. pause — action: media_pause | risk: safe
227. play or pause — action: media_play_pause | risk: safe
228. next song — action: media_next | risk: safe
229. previous song — action: media_previous | risk: safe
230. next track — action: media_next | risk: safe
231. previous track — action: media_previous | risk: safe
232. stop music — action: media_stop | risk: safe
233. play music — action: play_music | risk: safe
234. pause music — action: media_pause | risk: safe
235. open volume mixer — action: open_volume_mixer | risk: safe
236. increase brightness — action: brightness_up | risk: safe
237. decrease brightness — action: brightness_down | risk: safe
238. set brightness to <number> percent — action: set_brightness | risk: safe
### System, Power and Network

239. lock computer — action: lock | risk: confirm
240. lock screen — action: lock | risk: confirm
241. sleep computer — action: sleep | risk: confirm
242. restart computer — action: restart | risk: confirm
243. shut down computer — action: shutdown | risk: confirm
244. sign out — action: sign_out | risk: confirm
245. cancel shutdown — action: cancel_shutdown | risk: safe
246. show desktop — action: show_desktop | risk: safe
247. minimize all windows — action: minimize_all | risk: safe
248. restore all windows — action: restore_all | risk: safe
249. switch window — action: alt_tab | risk: safe
250. switch to next window — action: alt_tab | risk: safe
251. open task view — action: task_view | risk: safe
252. turn wifi on — action: wifi_on | risk: safe
253. turn wifi off — action: wifi_off | risk: safe
254. turn bluetooth on — action: bluetooth_on | risk: safe
255. turn bluetooth off — action: bluetooth_off | risk: safe
256. turn airplane mode on — action: airplane_on | risk: safe
257. turn airplane mode off — action: airplane_off | risk: safe
258. show wifi networks — action: show_wifi | risk: safe
259. disconnect wifi — action: wifi_off | risk: safe
260. enable dark mode — action: dark_mode_on | risk: safe
261. enable light mode — action: dark_mode_off | risk: safe
262. take screenshot — action: screenshot | risk: safe
263. take screenshot of window — action: screenshot_window | risk: safe
264. open clipboard history — action: clipboard_history | risk: safe
265. clear clipboard — action: clear_clipboard | risk: safe
266. empty recycle bin — action: empty_recycle_bin | risk: confirm
267. what time is it — action: tell_time | risk: safe
268. what is the date — action: tell_date | risk: safe
269. show battery status — action: battery_status | risk: safe
270. show system info — action: system_info | risk: safe
### Office and Documents

271. open microsoft word — action: launch_app | risk: safe
272. open microsoft excel — action: launch_app | risk: safe
273. open microsoft powerpoint — action: launch_app | risk: safe
274. open microsoft outlook — action: launch_app | risk: safe
275. open microsoft onenote — action: launch_app | risk: safe
276. create new word document — action: new_word_doc | risk: safe
277. open new blank document in word — action: new_word_doc | risk: safe
278. save document — action: save_doc | risk: safe
279. save document as — action: save_doc_as | risk: safe
280. close word document — action: close_doc | risk: safe
281. type <text> in word — action: type_in_word | risk: safe
282. type <text> in document — action: type_in_word | risk: safe
283. bold selected text in word — action: word_bold | risk: safe
284. italic selected text in word — action: word_italic | risk: safe
285. underline selected text in word — action: word_underline | risk: safe
286. increase font size in word — action: word_font_up | risk: safe
287. decrease font size in word — action: word_font_down | risk: safe
288. align text left in word — action: word_align_left | risk: safe
289. align text center in word — action: word_align_center | risk: safe
290. align text right in word — action: word_align_right | risk: safe
291. align text justify in word — action: word_align_justify | risk: safe
292. insert page break in word — action: word_page_break | risk: safe
293. insert table in word — action: word_insert_table | risk: safe
294. find text in document — action: word_find | risk: safe
295. replace text in document — action: word_replace | risk: safe
296. print document — action: print_doc | risk: safe
297. zoom in document — action: word_zoom_in | risk: safe
298. zoom out document — action: word_zoom_out | risk: safe
299. check spelling in document — action: word_spellcheck | risk: safe
300. create new excel workbook — action: new_excel_workbook | risk: safe
301. create new powerpoint presentation — action: new_ppt | risk: safe
302. open new email — action: new_email | risk: safe
303. send email — action: send_email | risk: confirm
### Files, Search and Productivity

304. search for file <file> — action: search_file | risk: safe
305. search files for <text> — action: search_file | risk: safe
306. create new folder — action: create_folder | risk: safe
307. create new text file — action: create_text_file | risk: safe
308. rename file — action: rename_file | risk: confirm
309. delete file — action: delete_file | risk: confirm
310. move file to recycle bin — action: recycle_file | risk: confirm
311. open downloads — action: open_folder | risk: safe
312. open documents — action: open_folder | risk: safe
313. open pictures — action: open_folder | risk: safe
314. open videos — action: open_folder | risk: safe
315. open recent files — action: open_recent | risk: safe
316. sort files by name — action: sort_by_name | risk: safe
317. sort files by date — action: sort_by_date | risk: safe
318. show hidden files — action: show_hidden_files | risk: safe
319. hide hidden files — action: hide_hidden_files | risk: safe
320. copy file path — action: copy_file_path | risk: safe
321. open sticky notes — action: launch_app | risk: safe
322. set timer for <number> minutes — action: set_timer | risk: safe
323. set alarm — action: set_alarm | risk: safe
324. open alarm — action: launch_app | risk: safe
325. check internet speed — action: internet_speed | risk: safe
326. show ip address — action: show_ip | risk: safe
### MS Word Extra

327. insert header in word — action: word_insert_header | risk: safe
328. insert footer in word — action: word_insert_footer | risk: safe
329. insert page number in word — action: word_insert_page_number | risk: safe
330. add bullet list in word — action: word_bullet_list | risk: safe
331. add numbered list in word — action: word_numbered_list | risk: safe
332. remove bullet list in word — action: word_remove_list | risk: safe
333. increase indent in word — action: word_indent_up | risk: safe
334. decrease indent in word — action: word_indent_down | risk: safe
335. insert image in word — action: word_insert_image | risk: safe
336. insert hyperlink in word — action: word_insert_hyperlink | risk: safe
337. insert date in word — action: word_insert_date | risk: safe
338. insert time in word — action: word_insert_time | risk: safe
339. change line spacing to single in word — action: word_spacing_single | risk: safe
340. change line spacing to double in word — action: word_spacing_double | risk: safe
341. set line spacing to 1.5 in word — action: word_spacing_1_5 | risk: safe
342. save document as pdf — action: save_doc_as_pdf | risk: safe
343. export document as pdf — action: save_doc_as_pdf | risk: safe
344. open recent document in word — action: word_open_recent | risk: safe
345. close all word documents — action: close_all_word_docs | risk: confirm
346. select paragraph in word — action: word_select_paragraph | risk: safe
347. select line in word — action: word_select_line | risk: safe
348. go to start of document — action: doc_start | risk: safe
349. go to end of document — action: doc_end | risk: safe
350. insert comment in word — action: word_insert_comment | risk: safe
351. track changes on in word — action: word_track_on | risk: safe
352. track changes off in word — action: word_track_off | risk: safe
353. show word count — action: word_count | risk: safe
354. insert horizontal line in word — action: word_insert_line | risk: safe
355. clear formatting in word — action: word_clear_formatting | risk: safe
356. change text color to red in word — action: word_color_red | risk: safe
357. change text color to blue in word — action: word_color_blue | risk: safe
358. change text color to black in word — action: word_color_black | risk: safe
359. highlight selected text in word — action: word_highlight | risk: safe
360. create table of contents in word — action: word_toc_create | risk: safe
361. update table of contents in word — action: word_toc_update | risk: safe
362. insert cover page in word — action: word_cover_page | risk: safe
363. set margins to narrow in word — action: word_margins_narrow | risk: safe
364. set margins to normal in word — action: word_margins_normal | risk: safe
365. change page orientation to portrait in word — action: word_portrait | risk: safe
366. change page orientation to landscape in word — action: word_landscape | risk: safe
367. insert section break in word — action: word_section_break | risk: safe
368. insert footnote in word — action: word_footnote | risk: safe
369. insert endnote in word — action: word_endnote | risk: safe
370. change font size to <number> in word — action: word_font_size | risk: safe
371. insert new paragraph in word — action: word_new_paragraph | risk: safe
### Daily Office

372. insert new row in excel — action: excel_insert_row | risk: safe
373. insert new column in excel — action: excel_insert_column | risk: safe
374. delete row in excel — action: excel_delete_row | risk: confirm
375. delete column in excel — action: excel_delete_column | risk: confirm
376. freeze top row in excel — action: excel_freeze_top | risk: safe
377. unfreeze panes in excel — action: excel_unfreeze | risk: safe
378. sort ascending in excel — action: excel_sort_asc | risk: safe
379. sort descending in excel — action: excel_sort_desc | risk: safe
380. apply filter in excel — action: excel_filter_on | risk: safe
381. remove filter in excel — action: excel_filter_off | risk: safe
382. sum selected cells in excel — action: excel_sum | risk: safe
383. format cells as currency in excel — action: excel_currency | risk: safe
384. format cells as percentage in excel — action: excel_percent | risk: safe
385. start slideshow in powerpoint — action: ppt_slideshow | risk: safe
386. next slide — action: ppt_next | risk: safe
387. previous slide — action: ppt_previous | risk: safe
388. go to first slide — action: ppt_first | risk: safe
389. go to last slide — action: ppt_last | risk: safe
390. reply to email — action: email_reply | risk: safe
391. forward email — action: email_forward | risk: safe
392. mark email as read — action: email_mark_read | risk: safe
393. archive email — action: email_archive | risk: safe
### Daily Use and Voice Control

394. start listening — action: voice_start | risk: safe
395. stop listening — action: voice_stop | risk: safe
396. pause listening — action: voice_pause | risk: safe
397. resume listening — action: voice_resume | risk: safe
398. start dictation — action: dictation_start | risk: safe
399. stop dictation — action: dictation_stop | risk: safe
400. what did you hear — action: show_last_transcript | risk: safe
401. show command list — action: show_commands | risk: safe
402. search commands for <text> — action: search_commands | risk: safe
403. open command history — action: open_history_log | risk: safe
404. clear command history — action: clear_history | risk: confirm
405. open start menu — action: open_start | risk: safe
406. open taskbar search — action: open_search_ui | risk: safe
407. open action center — action: open_action_center | risk: safe
408. open quick settings — action: open_quick_settings | risk: safe
409. open notification center — action: open_notifications_ui | risk: safe
410. convert text to uppercase — action: text_upper | risk: safe
411. convert text to lowercase — action: text_lower | risk: safe
412. speak selected text — action: speak_selection | risk: safe
413. set default browser to chrome — action: set_default_browser_chrome | risk: safe
414. set default browser to edge — action: set_default_browser_edge | risk: safe
415. set default browser to brave — action: set_default_browser_brave | risk: safe
416. set default ide to visual studio code — action: set_default_ide_vscode | risk: safe
417. set default ide to pycharm — action: set_default_ide_pycharm | risk: safe
418. repeat last command — action: repeat_last | risk: safe

## How to add a command later

1. Add one line above, in the right category.
2. Add the matching handler in the code (one function, one action).
3. Add it to the voice grammar list, so the speech recogniser can hear it.
4. Test it by typing it first, then by voice. Never ship a voice-only command.
