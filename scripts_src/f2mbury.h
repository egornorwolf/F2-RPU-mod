// Похороны после набега (1.3, Егор 2026-10-08): могила у частокола внизу слева, все жители собираются у нее,
// герой говорит, люди отвечают, потом все расходятся по местам. Копает прораб Хэнк (50 крышек не берет),
// если Хэнка нет — Тед с людьми. Тексты в f2mcfrm.msg, звать из скрипта Хэнка или Теда:
// bury_start(речь) после диалога и bury_step(fixed_param) в timed_event_p_proc.
// Подключать после define.h, command.h, sfall.h, f2mod.h, f2mset.h и f2mpay.h.
#ifndef F2MBURY_H
#define F2MBURY_H

#define BURY_GRAVE          (31760)     // x 160, y 158: внутри частокола у нижне-левой стены, между деревьями
#define PID_BURY_STONE      (33555445)  // Headstone (GRAVSTN1), блокирует клетку; проходимость проверена
#define PID_HANK            (PID_DOCK_WORKER)
#define PID_TED             (PID_AVERAGE_MERCHANT_MALE)
#define BURY_SPEECH_SKILL   (50)        // Красноречие: речь у могилы, дух еще +5%
#define BURY_TIMER          (70)        // timed_event: 71-73 ответы людей, 74 расходятся
#define GV_BURY_SPEECH      "f2mrbspc"  // какую речь сказал герой (ответы людей идут по таймеру)
#define BURY_MSG(n)         message_str(SCRIPT_F2MCFRM, n)

// Речь героя: 1 «одним из нас», 2 Красноречие удалось, 3 месть, 4 низкий Интеллект, 5 Красноречие не удалось
procedure bury_start(variable speech);
procedure bury_step(variable step);
procedure bury_resident(variable c);
procedure bury_speaker(variable pid, variable avoid);

// Где кто стоял до похорон. После загрузки сохранения посреди похорон массива нет: люди остаются у могилы
variable bury_was;

procedure bury_resident(variable c) begin
   // все живые на карте лагеря, кроме героя, его отряда, браминов и банды (команду жителей движок может поменять)
   return c != dude_obj and not is_critter_dead(c) and not obj_in_party(c) and obj_pid(c) != PID_BRAHMIN
      and obj_pid(c) != PID_RAIDER_MALE;
end

// Кто ответит: житель с этим PID (0 — любой, кроме Теда, Хэнка и avoid)
procedure bury_speaker(variable pid, variable avoid) begin
   variable c, all, n := 0;
   all := list_as_array(LIST_CRITTERS);
   foreach (c in all) begin
      if (bury_resident(c) and c != avoid) then begin
         if (pid and obj_pid(c) == pid) then return c;
         if (not pid and obj_pid(c) != PID_TED and obj_pid(c) != PID_HANK) then n += 1;
      end
   end
   if (pid or n == 0) then return 0;
   n := random(1, n);
   foreach (c in all) begin
      if (bury_resident(c) and c != avoid and obj_pid(c) != PID_TED and obj_pid(c) != PID_HANK) then begin
         n -= 1;
         if (n == 0) then return c;
      end
   end
   return 0;
end

procedure bury_start(variable speech) begin
   variable c, dead, places, d, r, k, t, i := 0, n := 0;
   set_sfall_global(GV_BURY_SPEECH, speech);
   dead := get_sfall_global_int(GV_RAID_DEAD);
   gfade_out(1);
   game_time_advance(2 * ONE_GAME_HOUR);
   // тело у ворот уносят, у частокола надгробие
   set_sfall_global(GV_SET_LEAVING, 1);
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (is_critter_dead(c) and obj_pid(c) == dead and tile_distance(tile_num(c), RAID_GATE_IN) < 8) then begin
         destroy_object(c);
         break;
      end
   end
   set_sfall_global(GV_SET_LEAVING, 0);
   if (not tile_contains_pid_obj(BURY_GRAVE, 0, PID_BURY_STONE)) then create_object(PID_BURY_STONE, BURY_GRAVE, 0);
   set_sfall_global(GV_RAID_BURY, 1);
   k := BURY_MORALE;
   if (speech == 2) then k += BURY_MORALE;
   set_sfall_global(GV_SET_MBONUS, get_sfall_global_int(GV_SET_MBONUS) + k);
   call set_short_morale(get_sfall_global_int(GV_SET_FSHORT), get_sfall_global_int(GV_SET_WSHORT));

   // места вокруг могилы по кольцам 2-5, кроме клеток у самого частокола
   places := temp_array(0, 0);
   r := 2;
   while (r <= 5) do begin
      d := 0;
      while (d < 6) do begin
         k := 0;
         while (k < r) do begin
            t := tile_num_in_direction(tile_num_in_direction(BURY_GRAVE, d, r), (d + 2) % 6, k);
            if (t % 200 <= 166 and t / 200 <= 166 and not obj_blocking_tile(t, 0, BLOCKING_TYPE_BLOCK)) then begin
               resize_array(places, n + 1);
               places[n] := t;
               n += 1;
            end
            k += 1;
         end
         d += 1;
      end
      r += 1;
   end
   // все жители к могиле, лицом к ней; где кто стоял — запомнить
   if (bury_was) then free_array(bury_was);
   bury_was := create_array_map;
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (bury_resident(c) and i < n) then begin
         bury_was[c] := tile_num(c);
         critter_attempt_placement(c, places[i], 0);
         anim(c, ANIMATE_ROTATION, rotation_to_tile(tile_num(c), BURY_GRAVE));
         i += 1;
      end
   end
   // герой у изголовья, со стороны лагеря
   critter_attempt_placement(dude_obj, tile_num_in_direction(BURY_GRAVE, 1, 1), 0);
   anim(dude_obj, ANIMATE_ROTATION, rotation_to_tile(tile_num(dude_obj), BURY_GRAVE));
   tile_set_center(BURY_GRAVE);
   gfade_in(1);
   float_msg(dude_obj, BURY_MSG(319 + speech), FLOAT_MSG_YELLOW);
   add_timer_event(self_obj, game_ticks(4), BURY_TIMER + 1);
end

// Ответы: Тед, кто-то из жителей, Хэнк (нет его — еще один житель); потом все расходятся
procedure bury_step(variable step) begin
   variable c, t, set;
   if (step <= BURY_TIMER or step > BURY_TIMER + 4) then return;
   step -= BURY_TIMER;
   set := get_sfall_global_int(GV_BURY_SPEECH);
   if (set == 5 or set < 1) then set := 1;
   if (step <= 3) then begin
      if (step == 1) then c := bury_speaker(PID_TED, 0);
      else if (step == 3) then c := bury_speaker(PID_HANK, 0);
      else c := 0;
      if (not c) then c := bury_speaker(0, 0);
      if (c) then float_msg(c, BURY_MSG(330 + (set - 1) * 3 + step - 1), FLOAT_MSG_NORMAL);
      add_timer_event(self_obj, game_ticks(4), BURY_TIMER + step + 1);
      return;
   end
   gfade_out(1);
   if (bury_was) then begin
      foreach (c: t in bury_was) begin
         if (not is_critter_dead(c)) then critter_attempt_placement(c, t, 0);
      end
      free_array(bury_was);
      bury_was := 0;
   end
   tile_set_center(tile_num(dude_obj));
   gfade_in(1);
   if (get_sfall_global_int(GV_BURY_SPEECH) == 2) then
      display_msg(BURY_MSG(346));
   else
      display_msg(BURY_MSG(345));
end

#endif
