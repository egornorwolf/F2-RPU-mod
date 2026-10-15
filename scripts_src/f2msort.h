// Сортировка существ по id объекта (постоянный порядок: id не меняется ни при разговоре, ни при загрузке).
// Жители лагеря (f2mhome.h), ополчение (f2mpost.h), гарнизон базы (f2mlair.ssl). Подключать после f2mod.h.
#ifndef F2MSORT_H
#define F2MSORT_H

procedure camp_sort_id(variable arr);

procedure camp_sort_id(variable arr) begin
   variable i, j, tmp, go;
   i := 1;
   while (i < len_array(arr)) do begin
      j := i;
      go := 1;
      // без «and» в условии цикла: sslc считает обе части, и при j = 0 полез бы в arr[-1]
      while (go) do begin
         go := 0;
         if (j > 0) then begin
            if (f2m_obj_id(arr[j - 1]) > f2m_obj_id(arr[j])) then begin
               tmp := arr[j];
               arr[j] := arr[j - 1];
               arr[j - 1] := tmp;
               j -= 1;
               go := 1;
            end
         end
      end
      i += 1;
   end
end

#endif
