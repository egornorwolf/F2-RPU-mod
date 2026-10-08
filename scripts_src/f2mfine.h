// Штраф за стрельбу по своим (Егор 2026-10-08). Прицельно ранил жителя — весь лагерь воюет, штраф 500;
// убил — 2000 (брамин 500). Ушел с карты и вернулся — лагерь опускает оружие (f2mcamp.ssl), а штраф требует
// староста Тед, без Теда — начальник охраны. Пути: заплатить; уговорить на половину (Красноречие 60, один раз);
// прийти позже с деньгами; отказаться — лагерь снова воюет. Пока штраф висит, с героем дел не ведут.
// Тексты в f2mcmst.msg (470-489). Подключать после define.h, command.h, sfall.h и f2mod.h.
#ifndef F2MFINE_H
#define F2MFINE_H

#define FINE_MSG(n)         message_str(SCRIPT_F2MCMST, n)
#define FINE_SPEECH         (60)
#define fine_due            (get_sfall_global_int(GV_CAMP_FINE) > 0)

procedure fine_ted_here;
procedure fine_node;
procedure fine_options;
procedure fine_pay;
procedure fine_talk;
procedure fine_later;
procedure fine_refuse;
procedure fine_end;

// Тед жив и стоит в лагере: штраф берет он, иначе начальник охраны
procedure fine_ted_here begin
   variable c;
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (obj_pid(c) == PID_AVERAGE_MERCHANT_MALE and not is_critter_dead(c) and not obj_in_party(c)) then return 1;
   end
   return 0;
end

procedure fine_node begin
   Reply(FINE_MSG(470) + get_sfall_global_int(GV_CAMP_FINE) + FINE_MSG(471));
   call fine_options;
end

procedure fine_options begin
   if (dude_caps >= get_sfall_global_int(GV_CAMP_FINE)) then
      NOption(FINE_MSG(472), fine_pay, 4);
   if (not get_sfall_global_int(GV_FINE_TALK)) then
      NOption(FINE_MSG(473), fine_talk, 4);
   NOption(FINE_MSG(474), fine_later, 4);
   NOption(FINE_MSG(475), fine_refuse, 4);
   if (dude_caps >= get_sfall_global_int(GV_CAMP_FINE)) then
      NLowOption(FINE_MSG(476), fine_pay);
   NLowOption(FINE_MSG(477), fine_later);
end

procedure fine_pay begin
   item_caps_adjust(dude_obj, -get_sfall_global_int(GV_CAMP_FINE));
   set_sfall_global(GV_CAMP_FINE, 0);
   set_sfall_global(GV_FINE_TALK, 0);
   Reply(FINE_MSG(478));
   NOption(FINE_MSG(479), fine_end, 4);
   NLowOption(FINE_MSG(479), fine_end);
end

procedure fine_talk begin
   set_sfall_global(GV_FINE_TALK, 1);
   if (has_skill(dude_obj, SKILL_SPEECH) >= FINE_SPEECH) then begin
      set_sfall_global(GV_CAMP_FINE, get_sfall_global_int(GV_CAMP_FINE) / 2);
      Reply(FINE_MSG(480) + get_sfall_global_int(GV_CAMP_FINE) + FINE_MSG(481));
   end else
      Reply(FINE_MSG(482) + get_sfall_global_int(GV_CAMP_FINE) + FINE_MSG(481));
   call fine_options;
end

procedure fine_later begin
   Reply(FINE_MSG(483));
   NOption(FINE_MSG(484), fine_end, 4);
   NLowOption(FINE_MSG(484), fine_end);
end

procedure fine_refuse begin
   set_sfall_global(GV_CARAVAN_HOSTILE, 1);
   Reply(FINE_MSG(485));
   NOption(FINE_MSG(486), fine_end, 4);
   NLowOption(FINE_MSG(486), fine_end);
end

procedure fine_end begin
end

#endif
