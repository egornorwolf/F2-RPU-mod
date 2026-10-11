// Сгенерировано tools/layout/levels_emit.py: невидимые блоки (block.frm) у костров, бака у колодца и насоса (0.9.7).
// Блок стоит, пока на месте его вещь (уровни зданий меняются). Не править руками.
#ifndef F2MSOLID_H
#define F2MSOLID_H
#define PID_SOLID      (33554560)
procedure solid_set(variable t, variable on) begin
   variable b;
   b := tile_contains_pid_obj(t, 0, PID_SOLID);
   if (on and not b) then create_object(PID_SOLID, t, 0);
   else if (not on and b) then destroy_object(b);
end
procedure solid_sync begin
   call solid_set(8938, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(8939, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(8940, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9136, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9137, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9138, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9139, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9140, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9335, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9336, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9337, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9338, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9339, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9340, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9535, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9536, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9537, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9538, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9539, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9540, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9541, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9737, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9738, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9739, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9740, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9741, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9748, tile_contains_pid_obj(10550, 0, 33555336));
   call solid_set(9749, tile_contains_pid_obj(10550, 0, 33555336));
   call solid_set(9750, tile_contains_pid_obj(10550, 0, 33555336));
   call solid_set(9938, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9939, tile_contains_pid_obj(9341, 0, 33554763));
   call solid_set(9946, tile_contains_pid_obj(10550, 0, 33555336));
   call solid_set(9947, tile_contains_pid_obj(10550, 0, 33555336));
   call solid_set(9948, tile_contains_pid_obj(10550, 0, 33555336));
   call solid_set(9949, tile_contains_pid_obj(10550, 0, 33555336));
   call solid_set(9950, tile_contains_pid_obj(10550, 0, 33555336));
   call solid_set(10147, tile_contains_pid_obj(10550, 0, 33555336));
   call solid_set(10148, tile_contains_pid_obj(10550, 0, 33555336));
   call solid_set(10149, tile_contains_pid_obj(10550, 0, 33555336));
   call solid_set(10150, tile_contains_pid_obj(10550, 0, 33555336));
   call solid_set(10151, tile_contains_pid_obj(10550, 0, 33555336));
   call solid_set(10347, tile_contains_pid_obj(10550, 0, 33555336));
   call solid_set(10348, tile_contains_pid_obj(10550, 0, 33555336));
   call solid_set(10349, tile_contains_pid_obj(10550, 0, 33555336));
   call solid_set(10350, tile_contains_pid_obj(10550, 0, 33555336));
   call solid_set(10548, tile_contains_pid_obj(10550, 0, 33555336));
   call solid_set(10549, tile_contains_pid_obj(10550, 0, 33555336));
   call solid_set(17084, tile_contains_pid_obj(17283, 0, 33555632));
   call solid_set(17282, tile_contains_pid_obj(17283, 0, 33555632));
   call solid_set(17284, tile_contains_pid_obj(17283, 0, 33555632));
   call solid_set(17483, tile_contains_pid_obj(17283, 0, 33555632));
   call solid_set(18481, tile_contains_pid_obj(18480, 0, 33555632));
   call solid_set(18679, tile_contains_pid_obj(18480, 0, 33555632));
   call solid_set(18680, tile_contains_pid_obj(18480, 0, 33555632));
   call solid_set(18681, tile_contains_pid_obj(18480, 0, 33555632));
   call solid_set(19884, tile_contains_pid_obj(20083, 0, 33555632));
   call solid_set(20082, tile_contains_pid_obj(20083, 0, 33555632));
   call solid_set(20084, tile_contains_pid_obj(20083, 0, 33555632));
   call solid_set(20283, tile_contains_pid_obj(20083, 0, 33555632));
   call solid_set(22906, tile_contains_pid_obj(23105, 0, 33555632));
   call solid_set(23104, tile_contains_pid_obj(23105, 0, 33555632));
   call solid_set(23106, tile_contains_pid_obj(23105, 0, 33555632));
   call solid_set(23305, tile_contains_pid_obj(23105, 0, 33555632));
end
#endif
