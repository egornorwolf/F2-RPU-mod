// Общая расстановка каравана «Хорошее место»: свободная клетка, Тед, охрана, брамины, фургоны
// и мирные переселенцы. Погибших в пути (f2mcdead.h) не ставим.
// Подключать после define.h, command.h, scenepid.h, sfall.h и f2mod.h.
#ifndef F2MCV_H
#define F2MCV_H

#include "f2mcdead.h"

procedure cv_free_tile(variable tile);
procedure cv_put(variable pid, variable sid, variable tile);
procedure cv_arm(variable who, variable weapon, variable ammo);
procedure cv_stims(variable who, variable n);
procedure cv_ted(variable tile);
procedure cv_guard(variable slot, variable tile);
procedure cv_brahmin(variable slot, variable tile);
procedure cv_corpse(variable slot, variable tile);
procedure cv_wagons(variable center);
procedure cv_civilians(variable center, variable kill);

// Ближайшая незанятая клетка (камни, фургоны и люди мешают)
procedure cv_free_tile(variable tile) begin
   variable d, r, t;
   if (not obj_blocking_tile(tile, 0, BLOCKING_TYPE_BLOCK)) then return tile;
   r := 1;
   while (r <= 3) do begin
      d := 0;
      while (d < 6) do begin
         t := tile_num_in_direction(tile, d, r);
         if (not obj_blocking_tile(t, 0, BLOCKING_TYPE_BLOCK)) then return t;
         d += 1;
      end
      r += 1;
   end
   return tile;
end

procedure cv_put(variable pid, variable sid, variable tile) begin
   variable obj;
   obj := create_object_sid(pid, cv_free_tile(tile), 0, sid);
   critter_add_trait(obj, TRAIT_OBJECT, OBJECT_TEAM_NUM, TEAM_CARAVAN);
   return obj;
end

// Оружие в руки (магазин движок заряжает полностью) и две пачки патронов
procedure cv_arm(variable who, variable weapon, variable ammo) begin
   variable item;
   item := create_object(weapon, 0, 0);
   add_obj_to_inven(who, item);
   wield_obj_critter(who, item);
   if (ammo) then add_mult_objs_to_inven(who, create_object(ammo, 0, 0), 2);
end

procedure cv_stims(variable who, variable n) begin
   add_mult_objs_to_inven(who, create_object(PID_STIMPAK, 0, 0), n);
end

// Тед Бернс. У его модели (торговец) нет анимаций пистолета, есть пистолет-пулемет:
// с пистолетом движок не дает ему стрелять.
procedure cv_ted(variable tile) begin
   variable obj;
   obj := cv_put(PID_AVERAGE_MERCHANT_MALE, SCRIPT_F2MCMST, tile);
   critter_add_trait(obj, TRAIT_OBJECT, OBJECT_AI_PACKET, AI_STORE_OWNER);
   call cv_arm(obj, PID_10MM_SMG, PID_10MM_JHP);
   call cv_stims(obj, 2);
   return obj;
end

// Охранник (CV_SLOT_GUARD) или охранница Сара (CV_SLOT_SARA), если жив
procedure cv_guard(variable slot, variable tile) begin
   variable obj;
   if (cv_is_dead(slot)) then return 0;
   obj := cv_put(cv_slot_pid(slot), SCRIPT_F2MCGRD, tile);
   if (slot == CV_SLOT_SARA) then
      call cv_arm(obj, PID_HUNTING_RIFLE, PID_223_FMJ);
   else
      call cv_arm(obj, PID_10MM_SMG, PID_10MM_JHP);
   call cv_stims(obj, 2);
   return obj;
end

// Брамин (место CV_SLOT_BRAHMIN или CV_SLOT_BRAHMIN + 1), если жив. В бою убегает (f2mcbrm).
procedure cv_brahmin(variable slot, variable tile) begin
   variable obj;
   if (cv_is_dead(slot)) then return 0;
   obj := cv_put(PID_BRAHMIN, SCRIPT_F2MCBRM, tile);
   critter_add_trait(obj, TRAIT_OBJECT, OBJECT_AI_PACKET, AI_ADDICT_WIMPY);
   return obj;
end

// Только что убитый член каравана (до прихода героя): труп без скрипта, место отмечено погибшим.
// Охранница остается при своих вещах.
procedure cv_corpse(variable slot, variable tile) begin
   variable obj;
   obj := cv_put(cv_slot_pid(slot), -1, tile);
   if (slot == CV_SLOT_SARA) then begin
      add_obj_to_inven(obj, create_object(PID_HUNTING_RIFLE, 0, 0));
      add_mult_objs_to_inven(obj, create_object(PID_223_FMJ, 0, 0), 2);
      call cv_stims(obj, 2);
      item_caps_adjust(obj, random(20, 50));
   end else if (slot >= CV_SLOT_CIV) then
      call cv_stims(obj, 1);
   kill_critter(obj, ANIM_fall_back_blood_sf);
   call cv_set_dead(slot);
   return obj;
end

// Три фургона вокруг стоянки мирных (настоящие фургоны караванов из игры)
procedure cv_wagons(variable center) begin
   variable t;
   t := tile_num_in_direction(center, 0, 6);
   if (not obj_blocking_tile(t, 0, BLOCKING_TYPE_BLOCK)) then begin
      Create_EW_Red_Caravan(t, 0)
   end
   t := tile_num_in_direction(center, 1, 7);
   if (not obj_blocking_tile(t, 0, BLOCKING_TYPE_BLOCK)) then begin
      Create_EW_Grey_Caravan(t, 0)
   end
   t := tile_num_in_direction(center, 2, 6);
   if (not obj_blocking_tile(t, 0, BLOCKING_TYPE_BLOCK)) then begin
      Create_EW_Red_Caravan(t, 0)
   end
end

// Мирные переселенцы: 3 мужчины, 4 женщины, 3 ребенка. Без оружия, в бою убегают.
// Свой стим у каждого считает скрипт мирного (f2mcciv), в инвентарь его не кладем.
// Ставим только живых; первые kill из них гибнут сразу (нападение началось до прихода героя).
procedure cv_civilians(variable center, variable kill) begin
   variable i := 0, obj, tile;
   while (i < 10) do begin
      if (not cv_is_dead(CV_SLOT_CIV + i)) then begin
         tile := tile_num_in_direction(center, i % 6, 2 + (i / 6) * 2);
         if (kill > 0) then begin
            call cv_corpse(CV_SLOT_CIV + i, tile);
            kill -= 1;
         end else begin
            obj := cv_put(cv_slot_pid(CV_SLOT_CIV + i), SCRIPT_F2MCCIV, tile);
            critter_add_trait(obj, TRAIT_OBJECT, OBJECT_AI_PACKET, AI_ADDICT_WIMPY);
            anim(obj, ANIMATE_ROTATION, random(0, 5));
         end
      end
      i += 1;
   end
end

#endif
