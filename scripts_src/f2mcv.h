// Общая расстановка каравана «Хорошее место»: свободная клетка, персонаж каравана, оружие,
// фургоны и мирные переселенцы. Подключать после define.h, command.h, scenepid.h, sfall.h и f2mod.h.
#ifndef F2MCV_H
#define F2MCV_H

procedure cv_free_tile(variable tile);
procedure cv_put(variable pid, variable sid, variable tile);
procedure cv_arm(variable who, variable weapon, variable ammo);
procedure cv_wagons(variable center);
procedure cv_civilians(variable center, variable first, variable count, variable dead);

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

procedure cv_arm(variable who, variable weapon, variable ammo) begin
   variable item;
   item := create_object(weapon, 0, 0);
   add_obj_to_inven(who, item);
   wield_obj_critter(who, item);
   if (ammo) then add_mult_objs_to_inven(who, create_object(ammo, 0, 0), 2);
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
// first/count — какие из десяти; dead — сколько из них уже мертвы (первые по списку)
procedure cv_civilians(variable center, variable first, variable count, variable dead) begin
   variable pids, i, n, obj, dist;
   pids := [PID_WEAK_PEASANT_MALE, PID_AVERAGE_PEASANT_FEMALE, PID_CHILD_MALE,
            PID_AVERAGE_PEASANT_MALE, PID_WEAK_PEASANT_FEMALE, PID_CHILD_FEMALE,
            PID_AVERAGE_PEASANT_FEMALE, PID_WEAK_PEASANT_MALE, PID_WEAK_PEASANT_FEMALE, PID_CHILD_MALE];
   n := 0;
   while (n < count) do begin
      i := first + n;
      dist := 2 + (i / 6) * 2;
      if (n < dead) then begin
         obj := cv_put(pids[i], -1, tile_num_in_direction(center, i % 6, dist));
         kill_critter(obj, ANIM_fall_back_blood_sf);
      end else begin
         obj := cv_put(pids[i], SCRIPT_F2MCCIV, tile_num_in_direction(center, i % 6, dist));
         critter_add_trait(obj, TRAIT_OBJECT, OBJECT_AI_PACKET, AI_ADDICT_WIMPY);
         anim(obj, ANIMATE_ROTATION, random(0, 5));
      end
      n += 1;
   end
end

#endif
