import { useDarkStore } from "@/stores/darkStore";
import React, { forwardRef } from "react";
import MiniMaxIconSVG from "./MiniMaxIcon";

export const MiniMaxIcon = forwardRef<SVGSVGElement, React.PropsWithChildren<{}>>(
  (props, ref) => {
    const isdark = useDarkStore((state) => state.dark).toString();
    return <MiniMaxIconSVG ref={ref} isdark={isdark} {...props} />;
  }
);

export default MiniMaxIcon;
