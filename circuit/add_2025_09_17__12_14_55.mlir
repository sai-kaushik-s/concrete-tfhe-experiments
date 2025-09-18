module {
  func.func @add(%arg0: !FHE.eint<9>, %arg1: !FHE.eint<9>) -> !FHE.eint<9> {
    %0 = "FHE.add_eint"(%arg0, %arg1) : (!FHE.eint<9>, !FHE.eint<9>) -> !FHE.eint<9>
    return %0 : !FHE.eint<9>
  }
}