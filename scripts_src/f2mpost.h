// Посты ополчения (Егор 2026-10-15, тест 0.9.10): ополченцы стоят не кучей у ворот, а по постам — двое по бокам
// проема южных ворот, стрелок за бетонным блоком поста, остальные цепью вдоль частокола, лицом наружу.
// Северный пост: двое дозорных у проема северных ворот (для антуража, бьют крыс как ополчение), пока стоит частокол.
// Места проверены tools/layout (свободны на всех уровнях зданий и с частоколом, до них можно дойти от въезда).
// Порядок ополченцев постоянный (по id объекта, как жители в f2mhome.h): кто на каком посту, не меняется.
// Охрана с базы (Егор 2026-10-15, 18:15): люди Кейна после мира и наемники Рика присылают в лагерь троих (base_guards).
// Подключать после f2mod.h, f2mcv.h, f2mraid.h, f2mlair.h и f2mhome.h.
#ifndef F2MPOST_H
#define F2MPOST_H

#define POST_N              (10)
#define GV_NPOST0           "f2mnpst0"  // id первого дозорного северного поста (0 — нет)
#define GV_NPOST1           "f2mnpst1"  // id второго

procedure post_tile(variable i);
procedure post_rot(variable i);
procedure mil_posts(variable walk);
procedure north_post;
procedure post_go(variable c, variable t, variable rot, variable walk);
procedure base_guards;

procedure post_tile(variable i) begin
   if (i == 0) then return 33103;   // (103, 165) левый край проема южных ворот
   if (i == 1) then return 33096;   // (96, 165) правый край
   if (i == 2) then return 32107;   // (107, 160) стрелок за блоком поста
   if (i == 3) then return 31500;   // (100, 157) на дороге за воротами
   if (i == 4) then return 32710;   // (110, 163) цепь вдоль частокола
   if (i == 5) then return 32691;   // (91, 163)
   if (i == 6) then return 33313;   // (113, 166)
   if (i == 7) then return 33288;   // (88, 166)
   if (i == 8) then return 31097;   // (97, 155)
   if (i == 9) then return 31704;   // (104, 158)
   if (i == 10) then return 6503;   // (103, 32) северный пост
   if (i == 11) then return 6497;   // (97, 32)
   return 0;
end

// Лицом наружу: у южных ворот вниз (2 юго-восток, 3 юго-запад, к проему), у северных вверх (0, 5)
procedure post_rot(variable i) begin
   if (i == 10) then return 0;
   if (i == 11) then return 5;
   if (post_tile(i) % 200 > 100) then return 2;
   return 3;
end

procedure post_go(variable c, variable t, variable rot, variable walk) begin
   if (tile_distance(tile_num(c), t) > 0) then begin
      if (walk and (tile_is_visible(tile_num(c)) or tile_is_visible(t))) then begin
         if (not anim_busy(c)) then animate_move_obj_to_tile(c, t, 0);
         return;
      end
      critter_attempt_placement(c, t, 0);
   end
   if (not anim_busy(c) and has_trait(TRAIT_OBJECT, c, OBJECT_CUR_ROT) != rot) then anim(c, ANIMATE_ROTATION, rot);
end

// Ополченцы по постам; walk 1 — из map_update (видимые идут пешком), 0 — вход на карту
procedure mil_posts(variable walk) begin
   variable c, arr, i, n0, n1, t;
   if (combat_is_initialized or get_sfall_global_int(GV_BURY_ON) or get_sfall_global_int(GV_CARAVAN_HOSTILE)) then return;
   n0 := get_sfall_global_int(GV_NPOST0);
   n1 := get_sfall_global_int(GV_NPOST1);
   arr := temp_array(0, 0);
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if ((obj_pid(c) == PID_MILITIA_MALE or obj_pid(c) == PID_MILITIA_FEMALE) and not is_critter_dead(c) and not obj_in_party(c)) then begin
         if (f2m_obj_id(c) == n0) then call post_go(c, post_tile(10), post_rot(10), walk);
         else if (f2m_obj_id(c) == n1) then call post_go(c, post_tile(11), post_rot(11), walk);
         else begin
            resize_array(arr, len_array(arr) + 1);
            arr[len_array(arr) - 1] := c;
         end
      end
   end
   call camp_sort_id(arr);
   i := 0;
   while (i < len_array(arr)) do begin
      if (i < POST_N) then call post_go(arr[i], post_tile(i), post_rot(i), walk);
      else begin
         // постов больше нет: вторая цепь в двух шагах за первой
         t := tile_num_in_direction(post_tile(i % POST_N), 0, 2);
         call post_go(arr[i], t, post_rot(i % POST_N), walk);
      end
      i += 1;
   end
end

// Северный пост ставится, когда стоит частокол (у него ворота и на севере). Погибший дозорный не возвращается
procedure north_post begin
   variable obj;
   if (not get_sfall_global_int(GV_FENCE) or get_sfall_global_int(GV_NPOST0)) then return;
   obj := cv_put(PID_MILITIA_MALE, SCRIPT_F2MCMIL, post_tile(10));
   call cv_arm(obj, PID_HUNTING_RIFLE, PID_223_FMJ);
   call cv_stims(obj, 1);
   set_sfall_global(GV_NPOST0, f2m_obj_id(obj));
   obj := cv_put(PID_MILITIA_MALE, SCRIPT_F2MCMIL, post_tile(11));
   call cv_arm(obj, PID_10MM_PISTOL, PID_10MM_JHP);
   call cv_stims(obj, 1);
   set_sfall_global(GV_NPOST1, f2m_obj_id(obj));
   display_msg("У северных ворот частокола встал дозор: двое ополченцев.");
end

// Трое с базы встают в ополчение лагеря (едят как ополченцы, стоят по постам mil_posts). Один раз:
// люди Кейна — сразу после мира (обещание Кейна, реплика 130), из тех, кто жив (на базе остается хотя бы один, кроме Кейна;
// карта карьера уберет их у себя, f2mlair.ssl); наемники — когда Рик прислал первых бойцов, сверх гарнизона базы
procedure base_guards begin
   variable n, i := 0, obj, ally;
   if (not lair_done or get_sfall_global_int(GV_BASE_SENT)) then return;
   ally := (get_sfall_global_int(GV_LAIR_HOW) == LAIR_HOW_ALLY);
   if (not ally and get_sfall_global_int(GV_BASE_INVITE) < 1) then return;
   n := BASE_SENT_N;
   if (ally) then begin
      // GV_BASE_GARR: живые свои в карьере при уходе героя (с Кейном); пока карту не покидал — все люди Кейна живы
      if (get_sfall_global_int(GV_BASE_GARR) > 0 and get_sfall_global_int(GV_BASE_GARR) - 2 < n) then n := get_sfall_global_int(GV_BASE_GARR) - 2;
      if (n <= 0) then begin
         set_sfall_global(GV_BASE_SENT, 2);
         return;
      end
   end
   set_sfall_global(GV_BASE_SENT, 1 + (not ally));   // 1 — карьер еще должен убрать троих у себя
   set_sfall_global(GV_BASE_SENT_N, n);
   while (i < n) do begin
      obj := cv_put(PID_MILITIA_MALE, SCRIPT_F2MCMIL, tile_num_in_direction(RAID_GATE_IN, (i + 3) % 6, 3));
      if (ally) then begin
         // налетчик Кейна (npc-cards.md): вид и оружие как в логове, у моделей NMLTBB и NMMAXZ есть анимации винтовки и пистолета-пулемета
         if (i % 2) then art_change_fid_num(obj, GANG_ART_JACKET);
         else art_change_fid_num(obj, GANG_ART_ARMOR);
         if (i % 2) then call cv_arm(obj, PID_10MM_SMG, PID_10MM_JHP);
         else call cv_arm(obj, PID_HUNTING_RIFLE, PID_223_FMJ);
      end else begin
         // наемник базы 1-го уровня (garrison_soldier в f2mlair.ssl): модель героя в кожаной броне
         art_change_fid_num(obj, FID_HMLTHR bwand 0xFFF);
         if (i % 2) then call cv_arm(obj, PID_10MM_SMG, PID_10MM_JHP);
         else call cv_arm(obj, PID_HUNTING_RIFLE, PID_223_FMJ);
      end
      call cv_stims(obj, 1);
      i += 1;
   end
   set_sfall_global(GV_SET_MILIT, get_sfall_global_int(GV_SET_MILIT) + n);
   if (ally) then display_msg(lair_msg(230) + n + lair_msg(231));
   else display_msg(lair_msg(232) + n + lair_msg(233));
end

#endif
