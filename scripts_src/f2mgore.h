// Следы боев в лагере (Егор 2026-10-08). Кровь и кости (PID_BLOOD_1-9) высыхают и пропадают через 2 дня.
// Трупы лежат до прихода собак: через сутки после того, как в лагере появились тела, приходят дикие собаки
// и едят их 2 дня, потом тел нет и собаки уходят. Убил собак — тела лежат до следующей стаи (еще через сутки).
// Героя нет на карте — все это идет «за кадром», при входе видно, что успело случиться.
// Погибшего жителя до похорон и Кейна до обыска собаки не трогают.
// Позже (по документам): трупы прибирает робот в кучу у свалки, едят наши звери и растения.
// Подключать в скрипт карты лагеря после f2mod.h, f2mcdead.h, f2mcv.h, f2mcamp.h и f2mraid.h.
#ifndef F2MGORE_H
#define F2MGORE_H

#define GV_GORE_HOUR        "f2mgoreh"  // когда пролилась кровь (час игры + 1, 0 — крови нет)
#define GV_DOG_HOUR         "f2mdogh0"  // когда придет стая (час игры + 1, 0 — ждать некого)
#define GV_DOG_ON           "f2mdogon"  // 1 = стая пришла (на карте или «за кадром»)
#define GV_FENCE_GORE       "f2mfncgo"  // 1 = тела с линии частокола уже вынесены за забор
#define GORE_HOURS          (48)
#define DOG_WAIT_HOURS      (24)
#define DOG_EAT_HOURS       (48)
#define DOG_COUNT           (3)
#define gore_now            (game_time / ONE_GAME_HOUR)

procedure gore_blood_mark;
procedure gore_update(variable entering);
procedure gore_is_food(variable c);
procedure gore_dogs;
procedure gore_fence_corpses;

// Звать, когда на карте пролилась кровь
procedure gore_blood_mark begin
   set_sfall_global(GV_GORE_HOUR, gore_now + 1);
end

procedure gore_is_food(variable c) begin
   if (not is_critter_dead(c) or obj_in_party(c) or c == dude_obj) then return 0;
   if (obj_pid(c) == get_sfall_global_int(GV_RAID_DEAD) and not get_sfall_global_int(GV_RAID_BURY)) then return 0;
   if (obj_pid(c) == PID_RAIDER_MALE and (obj_art_fid(c) bwand 0xFFF) == GANG_ART_BOSS and not get_sfall_global_int(GV_BOSS_NOTE)) then return 0;
   return 1;   // и убитые собаки тоже
end

// Живые собаки стаи
procedure gore_dogs begin
   variable c, n := 0;
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (obj_pid(c) == PID_WILD_DOG and not is_critter_dead(c)) then n += 1;
   end
   return n;
end

// Вход на карту (entering = 1) и map_update (вне боя). При герое на карте (в том числе после пропуска дней на стройке)
// собаки сначала приходят, и 2 дня еды считаются с их прихода: тела не пропадают, пока стаю не видно (0.9.6).
// «За кадром» (герой входит после отлучки) тела могут быть уже съедены
procedure gore_update(variable entering) begin
   variable c, all, food := 0, t, h, i, dog, any := 0;
   if (combat_is_initialized) then return;
   h := gore_now;
   all := list_as_array(LIST_ALL);
   // кровь и кости (в сохранениях до 0.6.6 кровь уже лежит без отметки: отсчет с этого входа)
   t := get_sfall_global_int(GV_GORE_HOUR);
   if (not t) then begin
      foreach (c in all) begin
         if (not t and obj_pid(c) >= PID_BLOOD_1 and obj_pid(c) <= PID_BLOOD_9) then begin
            call gore_blood_mark;
            t := h + 1;
         end
      end
   end
   if (t and h + 1 >= t + GORE_HOURS) then begin
      set_sfall_global(GV_GORE_HOUR, 0);
      foreach (c in all) begin
         if (obj_pid(c) >= PID_BLOOD_1 and obj_pid(c) <= PID_BLOOD_9 and elevation(c) == 0) then destroy_object(c);
      end
   end
   foreach (c in all) begin
      if (obj_type(c) == 1 and gore_is_food(c)) then begin
         food += 1;
         if (not any) then any := c;
      end
   end
   t := get_sfall_global_int(GV_DOG_HOUR);
   if (food == 0) then begin
      // есть нечего: стая уходит
      if (get_sfall_global_int(GV_DOG_ON) and gore_dogs > 0) then begin
         set_sfall_global(GV_SET_LEAVING, 1);
         foreach (c in all) begin
            if (obj_pid(c) == PID_WILD_DOG and not is_critter_dead(c)) then destroy_object(c);
         end
         set_sfall_global(GV_SET_LEAVING, 0);
      end
      set_sfall_global(GV_DOG_HOUR, 0);
      set_sfall_global(GV_DOG_ON, 0);
      return;
   end
   if (t == 0) then begin
      set_sfall_global(GV_DOG_HOUR, h + 1 + DOG_WAIT_HOURS);
      return;
   end
   if (h + 1 < t) then return;
   // стаю перебили: тела лежат до следующей
   if (get_sfall_global_int(GV_DOG_ON) and gore_dogs == 0 and h + 1 < t + DOG_EAT_HOURS) then begin
      set_sfall_global(GV_DOG_ON, 0);
      set_sfall_global(GV_DOG_HOUR, h + 1 + DOG_WAIT_HOURS);
      return;
   end
   if (h + 1 >= t + DOG_EAT_HOURS and (get_sfall_global_int(GV_DOG_ON) or entering)) then begin
      // съели: тел нет, стая ушла
      set_sfall_global(GV_SET_LEAVING, 1);
      foreach (c in all) begin
         if (obj_type(c) == 1 and (gore_is_food(c) or (obj_pid(c) == PID_WILD_DOG and not is_critter_dead(c)))) then destroy_object(c);
      end
      set_sfall_global(GV_SET_LEAVING, 0);
      set_sfall_global(GV_DOG_HOUR, 0);
      set_sfall_global(GV_DOG_ON, 0);
      return;
   end
   // стая пришла и ест
   if (not get_sfall_global_int(GV_DOG_ON)) then begin
      set_sfall_global(GV_DOG_ON, 1);
      set_sfall_global(GV_DOG_HOUR, h + 1);
      i := 0;
      while (i < DOG_COUNT) do begin
         dog := create_object_sid(PID_WILD_DOG, cv_free_tile(tile_num_in_direction(tile_num(any), random(0, 5), random(2, 3))), 0, -1);
         critter_add_trait(dog, TRAIT_OBJECT, OBJECT_TEAM_NUM, TEAM_DOG);
         anim(dog, ANIMATE_ROTATION, rotation_to_tile(tile_num(dog), tile_num(any)));
         i += 1;
      end
      display_msg("К телам у лагеря пришли дикие собаки.");
   end
end

// Частокол встал (f2mcfrm do_fence): тела на линии забора выносим за южную стену, в пустыню, где ходят набеги.
// Второго ряда забора нет (map-plan.md); если появится внешняя линия турелей, выносить за нее (Егор 2026-10-09)
#define GORE_FENCE_LO       (30)
#define GORE_FENCE_HI       (169)
#define GORE_OUT_Y          (176)
procedure gore_fence_corpses begin
   variable c, x, y, n := 0;
   if (not get_sfall_global_int(GV_FENCE) or get_sfall_global_int(GV_FENCE_GORE)) then return;
   set_sfall_global(GV_FENCE_GORE, 1);
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (is_critter_dead(c) and not obj_in_party(c) and elevation(c) == 0) then begin
         x := tile_num(c) % 200;
         y := tile_num(c) / 200;
         if (x >= GORE_FENCE_LO - 2 and x <= GORE_FENCE_HI + 2 and y >= GORE_FENCE_LO - 2 and y <= GORE_FENCE_HI + 2
             and (x <= GORE_FENCE_LO + 2 or x >= GORE_FENCE_HI - 2 or y <= GORE_FENCE_LO + 2 or y >= GORE_FENCE_HI - 2)) then begin
            if (x < 40) then x := 40 + n;
            if (x > 160) then x := 160 - n;
            move_to(c, cv_free_tile(GORE_OUT_Y * 200 + x), 0);
            n += 1;
         end
      end
   end
end

#endif
