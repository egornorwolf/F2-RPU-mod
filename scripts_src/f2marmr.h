// Боевая броня охране (Егор 2026-10-15). После стройки базы Рик предлагает взять у каравана боевую броню
// всей нашей охране (бывшим налетчикам и наемникам базы): цена одна за всех, 8000 (Егор 2026-10-15, тест 0.9.10).
// После оплаты броня (и вид, и сама броня) сразу у всех: охрана лагеря, бывшие налетчики, гарнизон базы.
// Вид меняем сами: движок переодевает в броню только героя. Модели героя HMCMBT/HFCMBT, у них все анимации оружия.
// Подключать после define.h и sfall.h.
#ifndef F2MARMR_H
#define F2MARMR_H

#define GV_BASE_ARMOR   "f2mbarmr"  // 1 = боевая броня охране куплена
#define ARMOR_TOTAL     (8000)      // боевая броня через караван на всех сразу (Егор 2026-10-15, тест 0.9.10)
#define armor_bought    (get_sfall_global_int(GV_BASE_ARMOR))
// Охрана лагеря: Рик, Сара, ополченцы и бывшие налетчики у поста
#define armor_is_guard(c)   (obj_pid(c) == PID_GUN_GUARD_MALE or obj_pid(c) == PID_GUN_GUARD_FEMALE \
                             or obj_pid(c) == PID_MILITIA_MALE or obj_pid(c) == PID_MILITIA_FEMALE)

procedure armor_dress(variable c);
procedure armor_dress_camp;

procedure armor_dress(variable c) begin
   variable it;
   it := critter_inven_obj(c, INVEN_TYPE_WORN);
   if (it) then begin
      if (obj_pid(it) == PID_COMBAT_ARMOR) then return;
   end
   it := create_object(PID_COMBAT_ARMOR, 0, 0);
   add_obj_to_inven(c, it);
   wield_obj_critter(c, it);
   if (get_critter_stat(c, STAT_gender) == GENDER_FEMALE) then art_change_fid_num(c, FID_HFCMBT bwand 0xFFF);
   else art_change_fid_num(c, FID_HMCMBT bwand 0xFFF);
end

// Карта лагеря: вся охрана в боевой броне
procedure armor_dress_camp begin
   variable c;
   if (not armor_bought) then return;
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (armor_is_guard(c) and not is_critter_dead(c) and not obj_in_party(c)) then call armor_dress(c);
   end
end

#endif
