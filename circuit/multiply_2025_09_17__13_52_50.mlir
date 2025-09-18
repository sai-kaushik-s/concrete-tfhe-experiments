module {
  func.func @multiply(%arg0: !FHE.eint<9>, %arg1: !FHE.eint<9>) -> !FHE.eint<16> {
    %0 = "FHE.mul_eint"(%arg0, %arg1) : (!FHE.eint<9>, !FHE.eint<9>) -> !FHE.eint<16>
    return %0 : !FHE.eint<16>
  }
}