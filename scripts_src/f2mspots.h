// Места жителей у построек: огороды 1-2 (работа), палатки 4-8 (дом). Создан tools/layout/spots_emit.py, руками не править.
#ifndef F2MSPOTS_H
#define F2MSPOTS_H

procedure lay_spot(variable slot, variable k);
procedure lay_night(variable tent, variable k);

procedure lay_spot(variable slot, variable k) begin
   if (slot == 1) then begin if (k == 0) then return 8125; return 8324; end
   if (slot == 2) then begin if (k == 0) then return 14125; return 14324; end
   if (slot == 3) then begin if (k == 0) then return 8475; return 8875; end
   if (slot == 4) then begin if (k == 0) then return 8291; return 8492; end
   if (slot == 5) then begin if (k == 0) then return 8261; return 8661; end
   if (slot == 6) then begin if (k == 0) then return 8056; return 8247; end
   if (slot == 7) then begin if (k == 0) then return 8440; return 8239; end
   return 0;
end

// Ночью: палатка 0-2 (стоят с начала) или 3-7 (палатки прораба, места построек 3-7), место у кровати 0-2
procedure lay_night(variable tent, variable k) begin
   if (tent == 0) then begin if (k == 0) then return 11077; if (k == 1) then return 11075; return 11076; end
   if (tent == 1) then begin if (k == 0) then return 10889; if (k == 1) then return 11091; return 11291; end
   if (tent == 2) then begin if (k == 0) then return 11465; if (k == 1) then return 11463; return 11464; end
   if (tent == 3) then begin if (k == 0) then return 8279; if (k == 1) then return 8277; return 8278; end
   if (tent == 4) then begin if (k == 0) then return 7890; if (k == 1) then return 8091; return 7892; end
   if (tent == 5) then begin if (k == 0) then return 7865; if (k == 1) then return 8065; return 7663; end
   if (tent == 6) then begin if (k == 0) then return 8050; if (k == 1) then return 8251; return 8052; end
   if (tent == 7) then begin if (k == 0) then return 8237; if (k == 1) then return 8439; return 8437; end
   return 0;
end

#endif
