package lu.fisch.canze.tools;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * Standalone utility that replays a raw ELM327 log, decodes the
 * responses using the CSV field definitions and stores the results
 * as an array of JSON objects {sid, name, value, unit}.
 */
public class LogReplayer {

    private static final short FIELD_TYPE_MASK   = 0x700;
    private static final short FIELD_TYPE_SIGNED = 0x100;
    private static final short FIELD_TYPE_STRING = 0x200;
    private static final short FIELD_TYPE_HEX    = 0x400;

    private static class FieldDef {
        final String sid;
        final String fromId;
        final int fromBit;
        final int toBit;
        final double resolution;
        final double offset;
        final int decimals;
        final String unit;
        final String requestId;
        final String responseId;
        final short options;
        final String name;

        FieldDef(String sid, String fromId, int fromBit, int toBit,
                 double resolution, double offset, int decimals,
                 String unit, String requestId, String responseId,
                 short options, String name) {
            this.sid = sid;
            this.fromId = fromId;
            this.fromBit = fromBit;
            this.toBit = toBit;
            this.resolution = resolution;
            this.offset = offset;
            this.decimals = decimals;
            this.unit = unit;
            this.requestId = requestId == null ? "" : requestId.toLowerCase();
            this.responseId = responseId == null ? "" : responseId.toLowerCase();
            this.options = options;
            this.name = name == null ? "" : name;
        }

        boolean isSigned() {
            return (options & FIELD_TYPE_MASK) == FIELD_TYPE_SIGNED;
        }
        boolean isString() {
            return (options & FIELD_TYPE_MASK) == FIELD_TYPE_STRING;
        }
        boolean isHexString() {
            return (options & FIELD_TYPE_MASK) == FIELD_TYPE_HEX;
        }
    }

    private static class Result {
        final String sid;
        final String name;
        final Object value;
        final String unit;
        Result(String sid, String name, Object value, String unit) {
            this.sid = sid;
            this.name = name;
            this.value = value;
            this.unit = unit;
        }
    }

    private static String escape(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private static List<FieldDef> loadFields(String dir) throws IOException {
        List<FieldDef> fields = new ArrayList<>();
        Files.walk(Paths.get(dir))
                .filter(p -> p.toString().endsWith("_Fields.csv"))
                .forEach(p -> {
                    try {
                        try (BufferedReader br = new BufferedReader(new FileReader(p.toFile()))) {
                            String line;
                            while ((line = br.readLine()) != null) {
                                line = line.trim();
                                if (line.isEmpty() || line.startsWith("#")) continue;
                                String[] parts = line.split(",", -1);
                                if (parts.length < 12) continue;
                                String sid = parts[0].trim();
                                String idHex = parts[1].trim().toLowerCase(Locale.ROOT);
                                int fromBit = Integer.parseInt(parts[2].trim());
                                int toBit = Integer.parseInt(parts[3].trim());
                                double res = Double.parseDouble(parts[4].trim());
                                double off = Double.parseDouble(parts[5].trim());
                                int dec = Integer.parseInt(parts[6].trim());
                                String unit = parts[7].trim();
                                String req = parts[8].trim().toLowerCase(Locale.ROOT);
                                String resp = parts[9].trim().toLowerCase(Locale.ROOT);
                                short opts = 0;
                                if (parts[10] != null && !parts[10].trim().isEmpty()) {
                                    try {
                                        opts = (short) Integer.parseInt(parts[10].trim(), 16);
                                    } catch (NumberFormatException e) {
                                        opts = 0;
                                    }
                                }
                                String name = parts.length > 11 ? parts[11].trim() : "";
                                if (sid.isEmpty()) {
                                    sid = String.format(Locale.ROOT, "%s.%d.%s", idHex, fromBit, resp);
                                } else {
                                    sid = sid.toLowerCase(Locale.ROOT);
                                }
                                fields.add(new FieldDef(sid, idHex, fromBit, toBit, res, off, dec, unit, req, resp, opts, name));
                            }
                        }
                    } catch (IOException e) {
                        throw new RuntimeException(e);
                    }
                });
        return fields;
    }

    private static String hexToBin(String hex) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < hex.length(); i += 2) {
            String b = hex.substring(i, Math.min(i + 2, hex.length()));
            int v = Integer.parseInt(b, 16);
            sb.append(String.format("%8s", Integer.toBinaryString(v)).replace(' ', '0'));
        }
        return sb.toString();
    }

    private static Object decodeField(FieldDef f, String payload) {
        String bin = hexToBin(payload);
        if (bin.length() <= f.toBit) return null;
        String sub = bin.substring(f.fromBit, f.toBit + 1);
        if (f.isString()) {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < sub.length(); i += 8) {
                int val = Integer.parseInt(sub.substring(i, Math.min(i + 8, sub.length())), 2);
                sb.append((char) val);
            }
            return sb.toString();
        } else if (f.isHexString()) {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < sub.length(); i += 8) {
                int val = Integer.parseInt(sub.substring(i, Math.min(i + 8, sub.length())), 2);
                sb.append(String.format("%02X", val));
            }
            return sb.toString();
        } else {
            long val = Long.parseLong(sub, 2);
            if (f.isSigned() && sub.charAt(0) == '1') {
                val = val - (1L << sub.length());
            }
            double calc = (val - f.offset) * f.resolution;
            double scale = Math.pow(10, f.decimals);
            return Math.round(calc * scale) / scale;
        }
    }

    private static void decodeMessage(String fromId, String requestId, String payload,
                                      Map<String, Result> results,
                                      Map<String, List<FieldDef>> index) {
        String key = fromId + "|" + requestId;
        List<FieldDef> candidates = index.get(key);
        if (candidates == null) return;
        for (FieldDef f : candidates) {
            if (!payload.startsWith(f.responseId)) continue;
            Object val = decodeField(f, payload);
            if (val != null) {
                results.put(f.sid, new Result(f.sid, f.name, val, f.unit));
            }
        }
    }

    public static void main(String[] args) throws IOException {
        if (args.length != 2) {
            System.err.println("Usage: LogReplayer <inputRawLog> <outputFile>");
            System.exit(1);
        }

        List<FieldDef> allFields = loadFields("app/src/main/assets/ZOE");
        Map<String, List<FieldDef>> index = new HashMap<>();
        for (FieldDef f : allFields) {
            String key = f.fromId + "|" + f.requestId;
            index.computeIfAbsent(key, k -> new ArrayList<>()).add(f);
        }

        Map<String, Result> results = new LinkedHashMap<>();

        try (BufferedReader br = new BufferedReader(new FileReader(args[0]))) {
            String line;
            String pending = null;
            String currentRespId = "";
            String currentRequest = "";
            while (true) {
                if (pending != null) {
                    line = pending;
                    pending = null;
                } else {
                    line = br.readLine();
                    if (line == null) break;
                }
                line = line.trim();
                if (line.startsWith(">")) {
                    String cmd = line.substring(1).trim();
                    String upper = cmd.toUpperCase(Locale.ROOT);
                    if (upper.startsWith("ATCRA")) {
                        currentRespId = cmd.substring(5).trim().toLowerCase(Locale.ROOT);
                    } else if (!upper.startsWith("AT")) {
                        if (cmd.matches("[0-9A-Fa-f]+") && cmd.length() > 2) {
                            currentRequest = cmd.substring(2).toLowerCase(Locale.ROOT);
                        } else {
                            currentRequest = cmd.toLowerCase(Locale.ROOT);
                        }
                    }
                } else if (line.startsWith("<")) {
                    String data = line.substring(1).trim().replace(" ", "");
                    String upper = data.toUpperCase(Locale.ROOT);
                    if (upper.startsWith("OK") || upper.startsWith("NO DATA") || upper.isEmpty() ||
                        !data.matches("[0-9A-Fa-f]+")) {
                        continue;
                    }
                    String payload;
                    if (data.length() >= 4 && data.substring(0,2).equalsIgnoreCase("10")) {
                        int totalLen = Integer.parseInt(data.substring(2,4),16);
                        payload = data.substring(4);
                        int needed = totalLen * 2;
                        while (payload.length() < needed) {
                            String next = br.readLine();
                            if (next == null) break;
                            next = next.trim();
                            if (!next.startsWith("<")) { pending = next; break; }
                            String ndata = next.substring(1).trim().replace(" ", "");
                            if (ndata.length() > 2) {
                                payload += ndata.substring(2);
                            }
                        }
                    } else {
                        int len = Integer.parseInt(data.substring(0,2),16);
                        payload = data.substring(2, Math.min(2 + len*2, data.length()));
                    }
                    decodeMessage(currentRespId.toLowerCase(Locale.ROOT),
                                  currentRequest.toLowerCase(Locale.ROOT),
                                  payload.toLowerCase(Locale.ROOT),
                                  results, index);
                }
            }
        }

        try (BufferedWriter bw = new BufferedWriter(new FileWriter(args[1]))) {
            bw.write("[\n");
            boolean first = true;
            for (Result r : results.values()) {
                if (!first) bw.write(",\n");
                first = false;
                bw.write("  {\"sid\": \"" + escape(r.sid) + "\", \"name\": \"" + escape(r.name) + "\", ");
                if (r.value instanceof String) {
                    bw.write("\"value\": \"" + escape(r.value.toString()) + "\"");
                } else {
                    bw.write("\"value\": " + r.value);
                }
                if (r.unit != null && !r.unit.isEmpty()) {
                    bw.write(", \"unit\": \"" + escape(r.unit) + "\"");
                }
                bw.write("}");
            }
            bw.write("\n]\n");
        }
    }
}
