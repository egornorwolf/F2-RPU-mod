// Места жителей у построек: огороды 1-2 (работа), палатки 4-8 (дом). Создан tools/layout/spots_emit.py, руками не править.
#ifndef F2MSPOTS_H
#define F2MSPOTS_H

procedure lay_spot(variable slot, variable k);

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

#endif
