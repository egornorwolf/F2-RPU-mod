// Кто из людей лагеря стоит на карте: ушедших убираем, вернувшихся ставим у костра.
// Зовут карта лагеря (при входе) и глобальный скрипт (герой в лагере: через затемнение, Егор 2026-10-08).
// Подключать после define.h, command.h, scenepid.h, sfall.h, f2mod.h, f2mcv.h, f2mcamp.h, f2mtlay.h и f2mset.h.
#ifndef F2MSYNC_H
#define F2MSYNC_H

procedure camp_sync_pid(variable pid);
procedure camp_sync_people;

// Сколько людей такого вида должно быть в лагере (живы и не ушли) и сколько стоит на карте.
// Лишних убираем, недостающих ставим у костра. Переселенцы одного вида взаимозаменяемы.
procedure camp_sync_pid(variable pid) begin
   variable i := CV_SLOT_SARA, want := 0, c, n := 0, obj;
   while (i < CV_SLOTS) do begin
      if (i != CV_SLOT_BRAHMIN and i != CV_SLOT_BRAHMIN + 1 and cv_slot_pid(i) == pid and set_here(i)) then want += 1;
      i += 1;
   end
   set_sfall_global(GV_SET_LEAVING, 1);
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (obj_pid(c) == pid and not is_critter_dead(c)) then begin
         n += 1;
         if (n > want) then destroy_object(c);
      end
   end
   set_sfall_global(GV_SET_LEAVING, 0);
   while (n < want) do begin
      if (pid == PID_GUN_GUARD_FEMALE) then
         call cv_guard(CV_SLOT_SARA, tile_num_in_direction(LAY_CHIEF, 2, 3));
      else begin
         obj := cv_put(pid, SCRIPT_F2MCCIV, tile_num_in_direction(LAY_FIRE, random(0, 5), random(2, 4)));
         critter_add_trait(obj, TRAIT_OBJECT, OBJECT_AI_PACKET, AI_ADDICT_WIMPY);
      end
      n += 1;
   end
end

procedure camp_sync_people begin
   call camp_sync_pid(PID_GUN_GUARD_FEMALE);
   call camp_sync_pid(PID_WEAK_PEASANT_MALE);
   call camp_sync_pid(PID_AVERAGE_PEASANT_MALE);
   call camp_sync_pid(PID_WEAK_PEASANT_FEMALE);
   call camp_sync_pid(PID_AVERAGE_PEASANT_FEMALE);
   call camp_sync_pid(PID_CHILD_MALE);
   call camp_sync_pid(PID_CHILD_FEMALE);
end

#endif
