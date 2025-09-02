export const metadata = { title: 'GraySpace Upscale', description: '2D → High-Res Upscale' };
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (<html lang="ko"><body><main>{children}</main></body></html>);
}
