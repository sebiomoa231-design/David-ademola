import DavidCommandCenter from "@/components/david-command-center";

export default async function Page({ params }: { params: Promise<{ slug?: string[] }> }) {
  const resolved = await params;
  const route = resolved.slug?.join("/") || "dashboard";
  return <DavidCommandCenter initialRoute={route} />;
}
